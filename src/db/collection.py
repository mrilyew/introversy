from peewee import TextField, IntegerField, AutoField, BooleanField, TimestampField, DeferredForeignKey, JOIN
from resources.globals import BaseModel, consts, time, model_to_dict, reduce, operator

class Collection(BaseModel):
    self_name = 'collection'

    id = AutoField()
    name = TextField(index=True,default='...')
    description = TextField(index=True,null=True)
    order = IntegerField(null=True,default=0)
    author = TextField(null=True,default=consts['pc_fullname'])
    frontend_type = TextField(default='list',null=False)
    json_info = TextField(index=True,null=True)
    preview_id = TextField(null=True)
    hidden = BooleanField(default=0)
    created_at = TimestampField(default=time.time())
    edited_at = TimestampField(null=True, default=0)

    @staticmethod
    def getAll():
        return Collection.select().where(Collection.hidden == 0).order_by(Collection.order)
    
    @staticmethod
    def getAllCount():
        return Collection.select().where(Collection.hidden == 0).count()
    
    @staticmethod
    def get(id):
        try:
            return Collection.select().where(Collection.id == id).get()
        except:
            return None
    
    def getApiStructure(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "order": self.order,
            "frontend_type": self.frontend_type,
            "preview": self.preview_id,
            "created": self.created_at,
            "edited": self.edited_at,
            "count": self.getItemsCount(),
        }
    
    def switch(self, to_switch):
        f_order = self.order
        s_order = to_switch.order

        self.order = s_order
        to_switch.order = f_order

        self.save()
        to_switch.save()

    def __fetchItems(self, query = None, columns_search = []):
        from db.entity import Entity
        from db.collection import Collection
        from db.relation import Relation

        DeferredForeignKey.resolve(Entity)
        DeferredForeignKey.resolve(Collection)

        items = (Relation
        .select(Relation, Collection, Entity)
        .where(Relation.parent_collection_id == self.id)
        .join(Collection, on=(Relation.child_collection_id == Collection.id), join_type=JOIN.LEFT_OUTER)
        .switch(Relation)
        .join(Entity, on=(Relation.child_entity_id == Entity.id), join_type=JOIN.LEFT_OUTER)
        .order_by(Relation.order)
        .where(Entity.hidden == 0))
        
        if query != None:
            query = query
            conditions = [] # litwin

            for column in columns_search:
                match column:
                    case "original_name":
                        conditions.append(
                            (Entity.original_name.contains(query)) | 
                            (Collection.name.contains(query))
                        )
                    case "display_name":
                        conditions.append(
                            (Entity.display_name.contains(query))
                        )
                    case "description":
                        conditions.append(
                            (Collection.description.contains(query)) |
                            (Entity.description.contains(query))
                        )
                    case "source":
                        conditions.append(
                            (Entity.source.contains(query))
                        )
                    case "index":
                        conditions.append(
                            (Entity.index_content.contains(query))
                        )
                    case "saved":
                        conditions.append(
                            (Entity.extractor_name.contains(query))
                        )
                    case "author":
                        conditions.append(
                            (Entity.author.contains(query)) |
                            (Collection.author.contains(query))
                        )
            if conditions:
                items = items.where(reduce(operator.or_, conditions))

        return items

    def getItems(self, offset = 0, limit = 10, query = None, columns_search = []):
        from db.entity import Entity

        items = self.__fetchItems(query=query,columns_search=columns_search)
        items = items.offset(offset).limit(limit)

        results = []
        for relation in items:
            if relation.child_collection_id:
                results.append(Collection(**model_to_dict(relation.child_collection_id)))

            if relation.child_entity_id:
                results.append(Entity(**model_to_dict(relation.child_entity_id)))
        
        return results

    def getItemsCount(self, query = None, columns_search = []):
        items = self.__fetchItems(query=query,columns_search=columns_search)
        
        return items.count()

    def addItem(self, entity):
        from db.relation import Relation

        if(self.hasItem(entity)):
            raise ValueError('Collection has that item')

        rel = Relation()
        rel.parent_collection_id = self.id
        if entity.__class__.__name__ == 'Collection':
            rel.child_collection_id = entity.id
        if entity.__class__.__name__ == 'Entity':
            rel.child_entity_id = entity.id

        rel.save()

    def removeItem(self, entity, delete_entity=True):
        from db.relation import Relation

        if(not self.hasItem(entity)):
            raise ValueError("Error: entity does not belows to collection")

        rel = Relation.delete().where(Relation.parent_collection_id == self.id)
        if entity.__class__.__name__ == 'Collection':
            rel = rel.where(Relation.child_collection_id == entity.id)
        if entity.__class__.__name__ == 'Entity':
            rel = rel.where(Relation.child_entity_id == entity.id)

        rel.execute()
        if delete_entity == True:
            entity.delete()

    def hasItem(self, entity):
        from db.relation import Relation

        rel = Relation.select().where(Relation.parent_collection_id == self.id)
        if entity.__class__.__name__ == 'Collection':
            rel = rel.where(Relation.child_collection_id == entity.id)
        if entity.__class__.__name__ == 'Entity':
            rel = rel.where(Relation.child_entity_id == entity.id)
        
        return rel.count() > 0
