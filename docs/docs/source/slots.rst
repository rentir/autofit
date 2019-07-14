===================================
The slot pseudo code description
===================================

The monitor pseudo code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The monitor is that piece of code that monitor the *buffer* folder. In this folder, producers
drops items and the monitor processes that items and plug them into the slots.
::
Upon arrival of new items, the slot table will be updated setting the new status as either 'updated' or
'failed'. It is not in the mandate of the Monitor to perform further processing, which is left for the SlotTable.flush()
method.

.. code-block:: python

	# MAX_PROCESSED_ITEMS is the maximum number of incoming items that
	# can be processed by this machine's instance
	MAX_PROCESSED_ITEMS = 10
	# This piece of code monitor for incomining files in the
	# buffer folder
	def process():
		processed_items=0
		with buffer_lock(): # wait until it gains access to the directory
			with mrp_lock():
				for f in glob.glob('*.json'):
					id = build_id_from(f)
					fname = build_file_name(f)
					if f.status == 'ok:
						SlotTable.updated(id, fname)
					else:
						SlotTable.failed(id)
					move_file_from_to(f, fname)
					processed_items += 1
					if processed_items == MAX_PROCESSED_ITEMS:
						break


The slots pseudo code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

	# This piece of code manages the update of the slots status
	# It is responsible to
	# 1. create new slots
	# 2. set the status to 'pending' or to 'invalid'
	# 3. It should also the the status to 'pending' and 'current'

	# The status 'updated' is necessary as it is not obvious that there are
	# spare producers able to accept the work.
	# The 'failed' state is needed too - only once all dependent slots have
	# been invalidated the state can go to 'invalid'
	SSTATUS = ['updated', 'current', 'stale', 'pending', 'failed', 'invalid']
	class SlotTable():
		"""
		This is the SLOT_TABLE.
		It has 3 public member functions:
		set_to_updated(s,fname) : set the status to 'updated'
		set_to_failed(s) : set the status to 'failed'
		flush() : process all the changes
		get_slot_id(s) : produce a unique slot it
		"""
		sid = None
		key = None # concatenation of keys
		slotname = None
		file = None # path to the file containing the data
		sstatus = None # this is the slot status in SSTATUS
		updatetime = None # the time stamp of last update

		def _slot_to_id(self,s):
			'''
			concatenate all the slot s attributes, joining by '.'
			'''
			res = s.name + "/" + str(s.date)
			values = []
			for k in s.keys():
				values.append(s.k)
			return res + '/' + sorted(valued).join('/')

		def _slot_exist(self,s):
			'''
			Return True is s is in the table, False otherwise
			'''
			id = _slot_to_id(s)
			sid = select('sid').where(sid == id)
			if len(sid) == 1:
				return True
			return False

		def _add_slot(self, s):
			'''
			Insert the slot s in the table with status='void' as return the sid
			'''
			if self._slot_exist(s):
				raise Exception("Slot already exist")
			id = create_id()
			SlotTable.update(date=s.data, slotname=s.name, sstatus='void', sid=id)
			return id

		def get_slot_id(self,s):
			'''
			concatenate all the slot s attributes, joining by '.'
			check if the sid is already available
			if it is, return it otherwise create a new one,
			insert into the table and return it
			TODO: how do we treat date? Should be a part of the key
			'''
			if self._slot_exist(s):
				return SlotTable.select('sid').where(sid == id).fetch_one()
			raise Exception("Slot not existing")

		def _update(self, s):
			'''
			The item was updated.
			All listeners are notified and then the item's status is set to 'pending'.
			The status of dependent slots are set to 'stale'
			NB: The slot id always exists as it is created once the producer accepts the incoming slots
			and update the SlotTree table
			'''
			sid = get_slot_id(s)
			listeners = get_listeners_of(s.name)
			for l in listeners:
				l.accept(s)
			set_to_pending(s)

		def _invalidate_dependents(self, sid):
			invalid_sids = SlotTree.select('sid2').where(SID1=sid)
			for sid in invalid_sids:
				set_to_stale(sid)
				for l in get_listener(sid.name):
					l.remove(sid)
				_invalidate_dependents(sid)

		def _failed(self,s)
			'''
			The item processing failed.
			The status of dependent slots are set to 'stale'
			'''
			self.set_to_failed(s)
			s.file = None
			sid = self._get_slot_id(s)
			_invalidate_dependents(sid)

		def set_to_updated(self, s, fname):
			sid = self._get_slot_id(s)
			self.where(sid==sid).update((status,file)=('updated',fname))

		def set_to_failed(self, s):
			sid = self._get_slot_id(s)
			self.where(sid==sid).update((status,file)=('updated',fname))

		def flush(self):
			for u in self.select(sid).where(status=='updated'):
				self._update(u)
			for f in self.select(sid).where(status=='updated'):
				self._failed(f)


The ProxyProducer pseudo code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

	class ProxyProducer(object):
		def __init__(self, producer):
			self.producer_name = producer
			self.required_slot_num = len(producer.required_slots)
			self.optional_slot_num = len(producer.optional_slots)
			self.keys = producers.keys

		def accepted(self, sid):
			"""
			Return True if the sid is already registered in the table
			"""

		def accept(self, slot):
			"""
			Take the incoming slot, join it with the producer keys and insert it in the
			producer table
			"""

		def launch(self):
			"""
			1. take all distinct combination of producers keys
			2. for each combination compute the number n of required slots
			3. if n>self.required_slot_num and at east one row is not pending then
				1. set all row to processing
				2. kick-off the producer task


The SlotTree pseudo code
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

	class SlotTree():
		SD1 = None
		SD2 = None
		def add(self, sd1, sd2):
			'''
			add the entry (sd1,sd2) to the table
			'''
