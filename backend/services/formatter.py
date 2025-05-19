class ResponseFormatter:
    def format(self, stats, insights, charts, table):
        return {'statistics': stats, 'insights': insights, 'charts': charts, 'tableData': table}