from gluon.html import TABLE, TR, TD, TH, DIV, SPAN, TEXTAREA, INPUT, SELECT, UL, CAT, LABEL, P
def custom_formstyle(form, fields):
        col_label_size = 4
        label_col_class = "col-sm-%d" % col_label_size
        col_class = "col-sm-%d" % (12 - col_label_size)
        offset_class = "col-sm-offset-%d" % col_label_size
        parent = TABLE(_class='table table-sm',
                       _style='margin-top: 1.5rem')
        for id, label, controls, help in fields:
            # wrappers
            _help = SPAN(help, _class='help-block')
            # embed _help into _controls
            _controls = DIV(controls, _help, _class="%s" % (col_class))
            if isinstance(controls, INPUT):
                if controls['_type'] == 'submit':
                    controls.add_class('btn btn-primary')
                    _controls = DIV(controls, _class="%s %s" %
                                    (col_class, offset_class))
                if controls['_type'] == 'button':
                    controls.add_class('btn btn-secondary')
                elif controls['_type'] == 'file':
                    controls.add_class('input-file')
                elif controls['_type'] in ('text', 'password'):
                    controls.add_class('form-control')
                elif controls['_type'] == 'checkbox' or controls['_type'] == 'radio':
                    controls.add_class('form-check-input')
                    label.add_class('form-check-label')
                    label.insert(0, controls)
                    _controls = DIV(
                        DIV(label, _help, _class="form-check"), _class="%s" % col_class)
                    label = DIV(_class="sm-hidden %s" % label_col_class)
                elif isinstance(controls, SELECT):
                    controls.add_class('custom-select')

                elif isinstance(controls, TEXTAREA):
                    controls.add_class('form-control')

            elif isinstance(controls, SPAN):
                _controls = P(controls.components,
                              _class="form-control-plaintext %s" % col_class)
            elif isinstance(controls, UL):
                for e in controls.elements("input"):
                    e.add_class('form-control')
            elif isinstance(controls, CAT) and isinstance(controls[0], INPUT):
                    controls[0].add_class('form-control')
            if isinstance(label, LABEL):
                label.add_class(
                    'form-control-label font-weight-bold %s' % label_col_class)

            parent.append(
                DIV(label, _controls, _class='form-group row', _id=id))
        return parent