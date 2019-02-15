from justa.models import CourtOrder


class JustaPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, dict):
            return item

        defaults = dict(item)
        defaults['source'] = spider.abbr
        data = {k: v for k, v in defaults.items() if k is not 'text'}

        _, created = CourtOrder.get_or_create(**data, defaults=defaults)
        msg = f'CourtOrder from {data["source"]} number {data["number"]}'
        if created:
            spider.logger.info(f'{msg} created')
        else:
            spider.logger.info(f'{msg} already exists')
