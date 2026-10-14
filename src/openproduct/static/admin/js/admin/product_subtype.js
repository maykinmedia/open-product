(function () {
    'use strict';

    const PRODUCTTYPE_SELECTOR = 'select[name="producttype"]';
    const SUBTYPE_SELECTOR = 'select[name="subtype"]';
    const DEFAULT_SUBTYPEN_URL = '/admin/producten/product/subtypen/';

    function setOptions(select, items) {
        const current = select.value;

        select.replaceChildren(
            new Option('---------', ''),
            ...items.map(({ id, name }) => new Option(name, id))
        );

        select.value = items.some(({ id }) => String(id) === current) ? current : '';
    }

    async function syncSubtypen(producttypeSelect) {
        const subtypeSelect = document.querySelector(SUBTYPE_SELECTOR);
        if (!subtypeSelect) return;

        const token = (producttypeSelect._syncToken = (producttypeSelect._syncToken || 0) + 1);

        if (!producttypeSelect.value) {
            setOptions(subtypeSelect, []);
            return;
        }

        const url = new URL(
            subtypeSelect.dataset.subtypenUrl || DEFAULT_SUBTYPEN_URL,
            window.location.origin
        );
        url.searchParams.set('producttype', producttypeSelect.value);

        subtypeSelect.disabled = true;
        try {
            const response = await fetch(url, {
                credentials: 'same-origin',
                headers: { Accept: 'application/json' },
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const items = await response.json();
            if (token === producttypeSelect._syncToken) setOptions(subtypeSelect, items);
        } catch (err) {
            console.error('Unable to retrieve subtypen', err);
        } finally {
            if (token === producttypeSelect._syncToken) subtypeSelect.disabled = false;
        }
    }

    // producttype is an autocomplete (select2) field, which triggers jQuery change
    // events instead of native ones, so listen through django.jQuery.
    window.django.jQuery(document).on('change', PRODUCTTYPE_SELECTOR, (event) => {
        syncSubtypen(event.target);
    });
})();
