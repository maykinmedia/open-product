function initWysimark(context = document) {
    const textareas = context.getElementsByClassName("wysimark-textarea");

    for (const textarea of textareas) {
        const container = textarea.nextElementSibling || document.createElement('div');
        container.className = 'wysimark-container';

        textarea.style.display = 'none';
        textarea.parentNode.insertBefore(container, textarea.nextSibling);

        createWysimark(container, {
            initialMarkdown: textarea.value, onChange: function (markdown) {
                textarea.value = markdown;
            }, height: '30em'
        });
    }
}


document.addEventListener('DOMContentLoaded', function () {
    initWysimark();
});


document.addEventListener('formset:added', (event) => {
    if (event.detail.formsetName === 'content_elementen') {
        initWysimark(event.target);
    }
});

