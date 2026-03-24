function arrayIncludes(array, element)
{
    for (var i = 0; i < array.length; i++)
        if (array[i] === element)
            return true

    return false
}

//
// Copies input as hidden field.
//
function copyFieldAsHidden(element, container)
{
    var containing_document = getDocument(container)
    function _copy(element, value)
    {
        var hidden = containing_document.createElement(
                         // IE doesn't understand dynamic name setting
                         userAgent.IE ? '<input name="' + element.name + '">' : 'INPUT'
                     )

        hidden.type = 'hidden'
        hidden.name = element.name
        hidden.value = (value == null ? element.value : value)

        container.appendChild(hidden)
    }

    switch (element.type) {
        case 'select-multiple':
            for (var i = 0; i < element.length; i++) {
                var option = element.options[i]
                if (option.selected)
                    _copy(element, option.value)
            }
            break

        case 'checkbox':
        case 'radio':
            if (! element.checked) break

        default:
            _copy(element)
    }
}

function setHiddenToField(hidden, field)
{
    switch (field.type) {
        case 'select-multiple':
            if (! hidden) 
                hidden = []
            else if (! hidden.length)
                hidden = [hidden]

            for (var i = 0; i < field.length; i++) {
                var option = field.options[i]
                option.selected = false

                for (var j = 0; j < hidden.length; j++)
                    if (option.value == hidden[j].value) {
                        option.selected = true
                        break
                    }
            }
            break

        case 'select':
            if (! hidden) {
                field.selectedIndex = -1
                break
            }
            for (var i = 0; i < field.length; i++) {
                var option = field.options[i]
                if (option.value == hidden.value) {
                    field.selectedIndex = i
                    break
                }
            }
            break

/*  too tough
            var option, j = 0
            for (var i = 0; i < hidden.length; i++) {
                for (; j < field.length && ((option = field.options[j]).value != hidden[i].value); j++)
                    option.selected = false;

                if (j < field.length)
                    option.selected = true;
            }
*/

        case 'checkbox':
        case 'radio':
            field.checked = (hidden != null)
            break

        default:
            field.value = hidden.value
    }

}

function copyFormAsHiddens(source, target, ignore_names)
{
    ignore_names = ignore_names || []
    
    for (var i = 0; i < source.elements.length; i++) {
        var field = source.elements[i]

        if (!field.name || arrayIncludes(ignore_names, field.name)) continue

        copyFieldAsHidden(field, target)
    }
}

function setHiddensToForm(container, target, ignore_names)
{
    ignore_names = ignore_names || []

    var form = container.parentNode
    for (var i = 0; i < target.elements.length; i++) {
        var field = target.elements[i]

        if (!field.name || arrayIncludes(ignore_names, field.name)) continue

        setHiddenToField(form.elements[field.name], field)
    }
}

var container_id = 'field_values:' + field_name
function getFieldsContainer(create)
{
    var root_document = editor.FCK.EditorWindow.parent.parent.document,
        container = root_document.getElementById(container_id)

    if (create && !container) {
        container = root_document.createElement('FIELDSET')
        container.id = container_id
        root_document.forms['edit'].appendChild(container)
    }

    return container
}
