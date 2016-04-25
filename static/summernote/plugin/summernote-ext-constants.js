(function (factory) {
  /* global define */
  if (typeof define === 'function' && define.amd) {
    // AMD. Register as an anonymous module.
    define(['jquery'], factory);
  } else if (typeof module === 'object' && module.exports) {
    // Node/CommonJS
    module.exports = factory(require('jquery'));
  } else {
    // Browser globals
    factory(window.jQuery);
  }
}(function ($) {

	/**
	* @class plugin.constants
	*
	* Initialize in the toolbar like so:
	*	toolbar: ['insert', ['constants']]
	*
	* Constants Plugin
	*/
  $.extend($.summernote.plugins, {
    /**
     * @param {Object} context - context object has status of editor.
     */
    'constants': function (context) {
      var self = this;

      // ui has renders to build ui elements - you can create a button with `ui.button`
      var ui = $.summernote.ui;

	  // add constants button
	  context.memo('button.constants', function () {
		// generate all the emojis
		var list = '';
		for (i = 0; i < constantsSet.length; i++) { list += '<li><a href="#">' + constantsSet[i] + '</a></li>'; }

        var $constantsList = ui.buttonGroup([
          ui.button({
            className: 'note-btn btn btn-default btn-sm dropdown-toggle',
            contents: '<i class="fa fa-star"></i> <i class="caret"></i>',
            tooltip: "Insert Constant",
            data: { toggle: 'dropdown' }
          }),
          ui.dropdown({
            className: 'note-check dropdown-line-height',
			contents: list,
			callback: function ($dropdown) {
                $dropdown.find('a').each(function () {
					$(this).click(function() {
					  var closest_editor = $(this).closest('div.note-editor').find('div.note-editable');
					  closest_editor.empty();
			          closest_editor.html($(this).html());
					});
                });
			}
          })
        ]).render();
		return $constantsList;
      });

      // This events will be attached when editor is initialized.
      this.events = {
        // This will be called after modules are initialized.
        'summernote.init': function (we, e) {

		  //console.log('summernote initialized', we, e);
        },
        // This will be called when user releases a key on editable.
        'summernote.keyup': function (we, e) {

          //console.log('summernote keyup', we, e);
        }
      };

      // This methods will be called when editor is destroyed by $('..').summernote('destroy');
      // You should remove elements on `initialize`.
		this.destroy = function () {};
    }
  });

  var constantsSet = [
    '<font color="darkred">None</font>',
    '<font color="darkgrey">Not available</font>',
    '<font color="darkgrey">Not applicable</font>'
  ];
}));
