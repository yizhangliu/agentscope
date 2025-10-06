<<<<<<< HEAD
// _static/language_switch.js

function toChinese() {
    window.location.href = "https://doc.agentscope.io/zh_CN";
}

function toEnglish() {
    window.location.href = "https://doc.agentscope.io";
}
=======
function switchV1Language() {
    if (window.location.href.includes("zh_CN")) {
        window.location.href = "https://doc.agentscope.io";
    } else {
        window.location.href = "https://doc.agentscope.io/zh_CN";
    }
}


function navigateToV0(version) {
    if (version === "v0") {
        const suffix = window.location.href.includes("zh_CN") ? "/zh_CN" : "/en";
        window.location.href = "https://doc.agentscope.io/v0" + suffix;
    }
}
>>>>>>> 6ee8fa352bcaf888adf82124e0e0a5c394454506
