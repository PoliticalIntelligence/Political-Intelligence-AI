from models.facebook_post import FacebookPost


class FacebookParser:
    """
    Responsible for extracting information
    from an already opened Facebook page.
    """

    def __init__(self, page):

        self.page = page

    def get_page_title(self):

        return self.page.title()

    def get_page_url(self):

        return self.page.url

    def create_dummy_post(self):

        """
        Temporary method.

        Later this will actually scrape Facebook.
        """

        return FacebookPost(
            leader_name="Unknown",
            page_name=self.get_page_title(),
            post_text="Parser Connected Successfully",
            post_url=self.get_page_url()
        )