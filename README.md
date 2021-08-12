# recipe_app_api
The Source Code of the Django web application called "recipe".


## Viewset vs APIView

I would call Viewset dynamic comparing to APIView because Viewset dynamically identifies what action is being performed, and it will link dynamically a particular url to the specific action. (example: "list" -> common_router -> .../list/  (they will all be dynamically generated in url)
                                                 "create" -> common_router -> .../create/..
                                                 "destroy" -> common_router -> .../delete/.. )
                                                 
On the other hand, APIView works on the standart way of how the HTTP methods work, meaning that each action needs to be manually linked to the specific url.  (example: "post" -> ../create/ (it should be done manually),
                "update" -> ../update/... )  
