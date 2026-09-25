(function () {
    'use strict';

    const TYPE_SELECTOR = 'select[name$="-facet_type"]';
    const DEFAULT_WAARDEN_URL = '/admin/producttypen/producttype/facet-waarden/';

    function getWaardeSelect(typeSelect) {
        const prefix = typeSelect.name.replace(/facet_type$/, '');
        return document.querySelector(`select[name="${prefix}facetwaarde"]`);
    }

    function setOptions(select, items) {
        const current = select.value;

        select.replaceChildren(
            new Option('---------', ''),
            ...items.map(({ id, name }) => new Option(name, id))
        );


        select.value = items.some(({ id }) => String(id) === current) ? current : '';
    }

    async function syncWaarden(typeSelect) {
        const waardeSelect = getWaardeSelect(typeSelect);
        if (!waardeSelect) return;

        const token = (typeSelect._syncToken = (typeSelect._syncToken || 0) + 1);

        if (!typeSelect.value) {
            setOptions(waardeSelect, []);
            return;
        }

        const url = new URL(
            typeSelect.dataset.waardenUrl || DEFAULT_WAARDEN_URL,
            window.location.origin
        );
        url.searchParams.set('facet_type', typeSelect.value);

        waardeSelect.disabled = true;
        try {
            const response = await fetch(url, {
                credentials: 'same-origin',
                headers: { Accept: 'application/json' },
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const items = await response.json();
            if (token === typeSelect._syncToken) setOptions(waardeSelect, items);
        } catch (err) {
            console.error('Unable to retrieve facet values', err);
        } finally {
            if (token === typeSelect._syncToken) waardeSelect.disabled = false;
        }
    }

    document.addEventListener('change', (event) => {
        if (event.target.matches(TYPE_SELECTOR)) syncWaarden(event.target);
    });
})();
