
MRP DB
----------
The MRP database is needed in order to:

* Synchronize the access to the data from different processes running of different machines
* Persist the slot's states
* Keep track of slot's dependency trees
* Keep track of running producers
* Joining the slot's data to be feed to the producers


In the following, the required table are listed

underlyings
^^^^^^^^^^^
* uid

* uname

* ric

* currency

* class

* type

* region

slot_classes
^^^^^^^^^^^^
Information of the slot, with columns:

* SLOT_NAME
          Name of the slot, for example MarketData.Vanilla.Totem
* SLOT_ID
          Identifier
* KEY_MAP
					This is a string made up of the slot's keys joined by '/, for example 'uname/region/type'

producer_classes
^^^^^^^^^^^^^^^^
Information on the producer.


SLOT_DEPS
^^^^^^^^^
Information on slots' dependencies:

* SLOT_ID
				the id of the slot
* DEP_ON_ID
				The slot SLOT_ID depends on
* REQUIRED
				The dependency is REQUIRED (1) or OPTIONAL (0)

SLOT_TABLE
^^^^^^^^^^
Keeps track of existing slots and register them with the SID.
Columns are:

* SLOT_ID
				id of the slot, a foreign key into SLOT_META
* DATE
				The valuation date
* SLOT_KEY
				This is a string made up of the slot's keys joined by '/, for
				example '0123456/EURO/INDEX'. The semantic is provided by they
				SLOT_META.KEY_MAP

* SID
 				unique identifier
* SSTATUS
				slot's status
* FILE
				path to the file containing the data



SLOT_TREE
^^^^^^^^^

Slot's dependency tree. This is required to invalidate downstream slots
(state set to 'stale') upon slot's update.

* SID1
				SID of the slot
* SID2
				SID of a slot depending on SID1

.. note:: This table is not a duplicate of SLOT_DEPS. The latter describes they
          dependencies between slots through methodologies, the former
          the actual dependency on the produced slots

RUNNING_PROD
^^^^^^^^^^^^

The table of the running producers

* PROD_NAME
				The producer name
* PID
				The producer unique id
* START_TIME
				The time when the producer was kicked off
* SID
				The slots being produced

SLOTs Tables
^^^^^^^^^^^^

Each slot is associated with a table with same name as the slot, with '.' replaced by '_'.
The tables have columns which are specific to the relative slot, apart a few which are fixed:

* DATE
				The valuation date
* SID
				The id from the SLOTS_TABLE
* LAST_UPDATED
				The last update time
* PRODUCER
				The producer that created the data
* PRIORITY
				The producer's priority
* Set of specific keys that identifies the item itself. In SQL parlance, these are *primary keys*.


PRODUCERs Tables
Each producers is associated with a list of slots which where notified to the producers and accepted.

* SID
				the id from the slot_table
* PSTATUS
				status of the processing ('pending','processing')

parcels_table
^^^^^^^^^^^^^
Contains the Information that the producer proxy need to bundle the slots into
parcels and kick-off tasks.

So far we have:

* pid
		The producer id
* sid
	  The slot id acknowledged by the producer
* uname, currency, class, type, region
		key from the slot, some could be None
