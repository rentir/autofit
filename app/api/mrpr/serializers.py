from autofit.app.restplus import api
from flask_restplus import fields


slot = api.model('Slot model', {'sid': fields.String(required=False,
                                                     description='The unique slot identifier'),
                                'name': fields.String(required=True, description="Slot's name"),
                                'keys': fields.String(required=True, description="Slot's keys"),
                                'date': fields.Date(required=True, description="Slot's valuation date"),
                                'priority': fields.Integer(required=True, description="Slot's priority"),
                                'state': fields.String(required=False, description="Slot's state"),
                                'updated_at': fields.DateTime(required=False, description="Slot's update time"),
                                'dbid': fields.String(required=True, description="DB id for the Slot's data")}
                 )

inputslot = api.model('InputSlot model', {'id_': fields.Integer(required=True, description="Table's primary key"),
                                          'pname': fields.String(required=True, description="Producer's name"),
                                          'sname': fields.String(required=True, description="Slot's name"),
                                          'sid': fields.String(required=True, description="Slot's sid"),
                                          'id1': fields.String(required=True, description="Asset1 id"),
                                          'ccy1': fields.String(required=True, description="Asset1 currency"),
                                          'id2': fields.String(required=True, description="Asset2 id"),
                                          'ccy2': fields.String(required=True, description="Asset2 currency"),
                                          'class_': fields.String(required=True, description="Asset class"),
                                          'type_': fields.String(required=True, description="Asset type"),
                                          'region': fields.String(required=True, description="region"),
                                          'date': fields.Date(required=True, description="Slot's date"),
                                          'last_updated': fields.DateTime(required=True,
                                                                          description="Last updated time"),
                                          'state': fields.String(required=True, description="InputSlot's state")}
                      )

producer = api.model('Producer model', {'pid': fields.String(required=False,
                                                             description='The unique producer identifier'),
                                        'pname': fields.String(required=True, description="Producer's name"),
                                        'keys': fields.String(required=True, description="Producers's keys"),
                                        'date': fields.Date(required=True, description="Valuation date"),
                                        'state': fields.String(required=False, description="Producer's state"),
                                        'args': fields.String(required=True, description="Data for producer execution"),
                                        'last_updated': fields.DateTime(required=False,
                                                                        description="Slot's update time")}
                     )

