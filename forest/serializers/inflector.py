import inflection

def caserize(attribute, opts):
    attribute = inflection.underscore(attribute)
    option = opts.get('key_for_attribute')

    if option == 'dash-case':
        return attribute
    elif option == 'lisp-case':
        return attribute
    elif option == 'kebab-case':
        return inflection.dasherize(attribute)
    elif option == 'underscore_case':
        return attribute
    elif option == 'snake_case':
        return attribute
    elif option == 'CamelCase':
        return inflection.camelize(attribute)
    elif option == 'camelCase':
        return inflection.camelize(attribute, false)
    else:
        return inflection.dasherize(attribute)

def pluralize(type_):
    return inflection.pluralize(type_)
