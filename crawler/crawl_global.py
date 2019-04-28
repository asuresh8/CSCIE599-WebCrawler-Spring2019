

class CrawlGlobal:
    context_ = None

    @staticmethod
    def set_context(context):
        context.logger.info('setting the context')
        CrawlGlobal.context_ = context
        if not CrawlGlobal.context_ :
            context.logger.info('failed setting the context')
    
    @staticmethod
    def context():
        return CrawlGlobal.context_