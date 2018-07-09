# TODO:
# pylint: Too many branches (20/12)
# pylint: Too many nested blocks (6/5)
def clean(self):
    try:
        # transition from 'N'/'O' to 'C' - all defined pilots must be selected
        # and product must be closed
        if self.instance.status in ('N', 'O') and self.cleaned_data['status'] == 'C':
            if self.instance.product.close_date is None:
                raise forms.ValidationError(u"Wyrób nie jest zamknięty")

            if self.instance.product.pilot_set.count() == 0:
                raise forms.ValidationError(u"Wyrób nie ma zdefiniowanych pilotów")

            for kind, name in PILOT_KINDS.items():
                if kind == 'N':
                    # pilots of kind 'N' are optional
                    continue
                if self.instance.get_pilot_choices(kind):
                    error = True
                    for pilot in self.cleaned_data.get('pilots', []):
                        if pilot.pilotkind == kind:
                            error = False
                            break
                    if error:
                        raise forms.ValidationError(u"Proszę wybrać pilot %s" % name)

        # transition from 'C' to 'P' - at least one pilot must be in 'P'
        # setting pilot to 'P' when contract stays is 'C' makes contract transit to 'P'
        if self.instance.status in ('C') and self.cleaned_data['status'] in ('C', 'P'):
            inprogress = False
            for pilot in self.instance.contract_pilots:
                if self.cleaned_data.get('pilot_status_' + str(pilot.pk), None) == 'P':
                    inprogress = True
                    break
            if self.cleaned_data['status'] == 'P' and not inprogress:
                raise forms.ValidationError(u"Proszę uruchomić co najmniej jeden pilot")
            if self.cleaned_data['status'] == 'C' and inprogress:
                # transit contract to 'P'
                self.cleaned_data['status'] = 'P'

        # transition from 'P' to 'G' - all pilots must be closed
        if self.cleaned_data['status'] == 'G':
            for pilot in self.instance.contract_pilots:
                if not self.cleaned_data.get('pilot_status_' + str(pilot.pk), None) in ('Z', 'M') \
                        and pilot.status not in ('Z', 'M'):
                    raise forms.ValidationError(u"Pilot %s jest w toku" %
                                                pilot.pilot.get_pilotkind_display())

        # transition from 'G' to 'Z' - at least one dispatch is required
        if self.instance.status in ('G') and self.cleaned_data['status'] == 'Z':
            if len(self.instance.dispatch_set.all()) == 0 \
                    and not self.cleaned_data['dispatch_number']:
                raise forms.ValidationError("Proszę podać numer WZ lub faktury")

        return self.cleaned_data
    except forms.ValidationError as ex:
        self.cleaned_data['status'] = self.instance.status
        raise ex
