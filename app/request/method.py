from enum import Enum


class Method(Enum):
    HEAD = 'head'
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'
    TRACE = 'trace'
    OPTIONS = 'options'
    PATCH = 'patch'
