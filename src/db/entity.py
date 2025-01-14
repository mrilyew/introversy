from resources.globals import consts, time, operator, reduce, Path
from peewee import TextField, BigIntegerField, AutoField, BooleanField, TimestampField
from resources.globals import BaseModel, json5

class Entity(BaseModel):
    self_name = 'entity'
    
    id = AutoField() # Absolute id
    format = TextField(null=True) # File extension
    original_name = TextField(default='N/A',null=False) # Name of file that been uploaded, hidden. Set by extractor
    display_name = TextField(index=True,default='N/A') # Name that shown in list. Set by api
    description = TextField(index=True,null=True) # Description of entity. Set by api
    source = TextField(null=True) # Source of content (URL or path). Set by extractor
    filesize = BigIntegerField(default=0) # Size of file in bytes. Set by api
    index_content = TextField(null=True) # Content that will be used for search. Set by extractor. Duplicates "json_info" but without keys.
    json_info = TextField(index=True,null=True) # Additional info in json (ex. video name)
    frontend_data = TextField(null=True) # Info that will be used in frontend. Set by frontend.
    extractor_name = TextField(null=True,default='base') # Extractor that was used for entity
    preview = TextField(null=True) # Preview in format photo:{path}
    pinned = BooleanField(default=0) # Unused
    hidden = BooleanField(default=0) # Is softly deleted
    author = TextField(null=True,default=consts['pc_fullname']) # Author of entity 🤫
    created_at = TimestampField(default=time.time())
    edited_at = TimestampField(null=True, default=0)

    def deleteFile(self):
        Path(self.getPath()).unlink()
    
    def delete(self, delete_file=True):
        if delete_file == True:
            self.deleteFile()

        self.hidden = 1
        self.save()

    def getApiStructure(self):
        json_info = getattr(self, "json_info", "{}")
        if json_info == None:
            json_info = "{}"
        
        return {
            "id": self.id,
            "format": self.format,
            "original_name": self.original_name,
            "display_name": self.display_name,
            "description": self.description,
            "filesize": self.filesize,
            "source": self.source,
            "index_content": self.index_content,
            "json_info": json5.loads(json_info),
            "frontend_data": self.frontend_data,
            "pinned": self.pinned,
            "created": self.created_at,
            "edited": self.edited_at,
            "author": self.author,
            "path": self.getPath(),
        }
    
    def getPath(self):
        storage = consts['cwd'] + '\\storage'
        collection_path = storage + '\\collections\\' + str(self.id)
        entity_path = collection_path + '\\' + str(self.id) + '.' + str(self.format)

        return entity_path
    
    def getDirPath(self, need_check = True):
        storage_path = consts['cwd'] + '\\storage'
        collection_path = storage_path + '\\collections\\' + str(self.id)
        coll_path = Path(collection_path)

        if need_check == True and coll_path.exists() == False:
            coll_path.mkdir(parents=True, exist_ok=True)

        return collection_path
    
    @staticmethod
    def fetchItems(query = None, columns_search = []):
        items = Entity.select().where(Entity.hidden == 0)
        conditions = []

        for column in columns_search:
            match column:
                case "original_name":
                    conditions.append((Entity.original_name.contains(query)))
                case "display_name":
                    conditions.append((Entity.display_name.contains(query)))
                case "description":
                    conditions.append((Entity.description.contains(query)))
                case "source":
                    conditions.append((Entity.source.contains(query)))
                case "index":
                    conditions.append((Entity.index_content.contains(query)))
                case "saved":
                    conditions.append((Entity.extractor_name.contains(query)))
                case "author":
                    conditions.append((Entity.author.contains(query)))
        
        if conditions:
            items = items.where(reduce(operator.or_, conditions))
        
        return items.order_by(Entity.id.desc())
    
    @staticmethod
    def get(id):
        try:
            return Entity.select().where(Entity.id == id).where(Entity.hidden == 0).get()
        except:
            return None
