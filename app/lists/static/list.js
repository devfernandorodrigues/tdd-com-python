window.Superlists = {}

window.Superlists.updateItems = function (url) {
  $.get(url).done(function (response) {
    var rows = ''

    response.forEach(function (row, index) {
      rows +=  '\n<tr><td>' + (index+1) + ': ' + row.text + '</td></tr>'
    })

    $('#id_list_table').html(rows)
  })
}

window.Superlists.initialize = function(url) {
  $('input[name="text"]').on('keypress', function () {
    $('.has-error').hide()
  })

  if (url) {
    window.Superlists.updateItems(url)
  }


  var form = $('#id_item_form')
  form.on('submit', function (event) {
    event.preventDefault()

    if (url) {
      $.post(url, {
        'text': form.find('input[name="text"]').val(),
        'csrfmiddlewaretoken': form.find('input[name="csrfmiddlewaretoken"]').val()
      }).done(function () {
        $('.has-error').hide()
        window.Superlists.updateItems(url)
      }).fail(function (response) {
        $('.has-error').show()
        if (response.responseJSON.error) {
          $('.has-error .help-block').text(response.responseJSON.error)
        } else {
          $('.has-error .help-block').text('something went wrong')
        }
      })
    }
  })
}
