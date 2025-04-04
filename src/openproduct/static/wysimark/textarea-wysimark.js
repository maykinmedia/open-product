document.addEventListener("DOMContentLoaded", function () {
    const textareas = document.getElementsByClassName("wysimark-textarea");

    for (const textarea of textareas) {
        const container = document.createElement('div');
        container.id = "wysimark-container";

        textarea.style.display = 'none';
        textarea.parentNode.insertBefore(container, textarea.nextSibling);

        createWysimark(container, {
            initialMarkdown: textarea.value,
            onChange: function (markdown) {
                textarea.value = markdown;
            },
            height: "30em",
        });
    }
});
