from database import Base, engine
from marshmallow import Schema, fields, ValidationError, pre_load

class RidbFacilities(Base):
    __tablename__ = 'ridb_facilities_orig'
    __table_args__ = {'autoload':True,'autoload_with': engine}

class RidbCampsites(Base):
    __tablename__ = 'ridb_campgrounds_orig'
    __table_args__ = {'autoload':True, 'autoload_with': engine}

class RidbFacilitiesSchema(Schema):
    index = fields.Int()
    facilityadaaccess = fields.Str()
    facilitydescription = fields.Str()
    facilitydirections = fields.Str()
    facilityemail = fields.Str()
    facilityid = fields.Int()
    facilitylatitude = fields.Float()
    facilitylongitude = fields.Float()
    facilitymapurl = fields.Str()
    facilityname = fields.Str()
    facilityphone = fields.Str()
    facilityreservationurl = fields.Str()
    facilitytypedescription = fields.Str()
    facilityusefeedescription = fields.Str()
    keywords = fields.Str()
    lastupdateddate = fields.Str()
    legacyfacilityid = fields.Str()
    orgfacilityid = fields.Str()
    staylimit = fields.Float()
    acquisitiondate = fields.Str()
    facilityindex = fields.Int()
