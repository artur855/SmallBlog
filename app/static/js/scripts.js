$('.close-icon').on('click',function() {
  $(this).closest('.card').fadeOut();
})

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})
