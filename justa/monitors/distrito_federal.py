from spidermon import Monitor, MonitorSuite, monitors


@monitors.name('Distrito Federal')
class DistritoFederalMonitor(Monitor):

    @monitors.name('Minimum number of items')
    def test_minimum_number_of_items(self):
        items_extracted = self.data.stats.get('item_scraped_count', 0)
        self.assertGreaterEqual(items_extracted, 433)


class DistritoFederalMonitorSuite(MonitorSuite):
    monitors = [DistritoFederalMonitor]
