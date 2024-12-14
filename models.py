# This file is optional. You can define schemas here if needed for documentation or future reference.

TodoSchema = {
    "userId": "ObjectId",
    "task": "String",
    "completed": "Boolean",
    "createdAt": "Date",
}

UserSchema = {
    "email": "String",
    "password": "String",
}