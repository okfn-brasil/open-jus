from justa import items, models


class JustaPipeline(object):

    @staticmethod
    def get_model(item):
        mapping = {
            items.CourtOrder: models.CourtOrder,
            items.CourtOrderESAJ: models.CourtOrderESAJ
        }
        return mapping.get(type(item))

    def process_item(self, item, spider):
        if isinstance(item, dict):
            return item

        defaults = dict(item)
        defaults['source'] = spider.name
        data = {k: v for k, v in defaults.items()}

        _, created = model.get_or_create(**data, defaults=defaults)
        msg = f'Court order {data["number"]} from {data["source"]}'
        status = 'created' if created else 'already exists'
        spider.logger.info(f'{msg} {status}')
        return item
