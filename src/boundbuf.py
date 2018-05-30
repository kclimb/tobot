import threading

class BoundedBuffer:

	def insert(self, items):
		return None

	def remove(self):
		return None

class ArrayBuffer:

	def __init__(self, size):
		self.max_capacity = size
		self.capacity = 0
		self.buf = []
		self.ind_start = 0
		self.ind_end = 0
		lock = threading.Lock()
		self.cond_empty = threading.Condition(lock)
		self.cond_full = threading.Condition(lock)

		# Make the list a fixed size. Nothing is appended or removed from here on
		# TODO: this is bad (though not terrible) if size is big. Fix so that
		# buffer lazily approaches max capacity
		for _ in xrange(size):
			self.buf.append(None)

	def insertMulti(self, items):
		num_items = len(items)
		cur_inserted = 0

class ListBuffer:

	def __init__(self, size = 256):
		self.max_capacity = size
		self.buf = []
		lock = threading.Lock()
		self.cond_empty = threading.Condition(lock)
		self.cond_full = threading.Condition(lock)

	def insertMulti(self, items):
		"""
		Unfinished
		"""
		self.cond_full.acquire()

		num_items = len(items)
		if num_items <= self.max_capacity - len(self.buf):
			self.buf.extend(items)
		else:
			inserted = 0
			while inserted < num_items:
				pass


		self.cond_full.release()
		self.lock.release()

	def insert(self, item):
		self.cond_full.acquire()

		while len(self.buf) == self.max_capacity:
			# We can give these locks up in the same order we acquired them because
			# nowhere does a thread try to acquire cond_full if it hasn't already
			# acquired cond_empty. Therefore, only the thread holding cond_empty
			# can possibly wait to acquire cond_full, which it will receive when
			# the current thread is done with cond_full on the next line
			print 'Full!'
			self.cond_full.wait()

		self.buf.append(item)
		self.cond_empty.notify()
		self.cond_full.release()

	def remove(self):
		self.cond_empty.acquire()

		while len(self.buf) == 0:
			print 'Empty!'
			self.cond_empty.wait()

		elem = self.buf.pop(0)
		self.cond_full.notify()
		self.cond_empty.release()
		return elem

#Some tests
TEST_COUNT = 500
flag = threading.Event()
def mthread(buf):
	for i in xrange(TEST_COUNT):
		buf.insert(i)

def tthread(buf):
	while not flag.is_set():
		# Condition is buggy since other threads may be waiting on remove() when flag gets set
		x = buf.remove()
		if not flag.is_set():
			if x == TEST_COUNT - 1:
				flag.set()
				# buf.cond_empty.acquire()
				# buf.cond_empty.notifyAll()
				# buf.cond_empty.release()
			print x

makers = []
takers = []
buf = ListBuffer(32)

makers.append(threading.Thread(None, mthread, 'm1', (buf), {}))
takers.append(threading.Thread(None, tthread, 't1', (buf), {}))
makers[0].start()
takers[0].start()

# makers[0].join()
# takers[0].join()
# print '1m1t pass'
# flag.clear()

# makers[0] = threading.Thread(None, mthread, 'm1', (buf,), {})
# takers[0] = threading.Thread(None, tthread, 't1', (buf,), {})

# for i in xrange(2, 5):
# 	takers.append(threading.Thread(None, tthread, 't' + str(i), (buf,)))

# for i in xrange(len(takers)):
# 	takers[i].start()
# makers[0].start()

# makers[0].join()
# print 'beep'
# for i in xrange(len(takers)):
# 	takers[i].join()
# 	print 'bop'
# print '1m4t pass'