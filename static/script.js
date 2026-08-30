// رسالة ترحيبية تفاعلية عند دخول المنصة
console.log("أهلاً بك يا بشمهندس ميدو في منصة البكالوريا مع ميدو 🚀");

// تأثير بسيط عند الضغط على الأزرار
document.addEventListener("DOMContentLoaded", function() {
    const buttons = document.querySelectorAll('.btn-custom');
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            console.log("تم النقر على زر تفاعلي!");
        });
    });
});
