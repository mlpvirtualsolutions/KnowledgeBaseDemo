url_mapper = {
    "meridian" : "[n8n webhook url]",

}


from urldict import url_mapper

if not authenticated:
    user_details = login_flow()
if authenticated:
    serve_main_page(user_details)

def serve_main_page(user_details):
    n8n_url = url_mapper[user_details['company']]
    # main page code here
    pass
