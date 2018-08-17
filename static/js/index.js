$(function () {
    // http://127.0.0.1:8000/path/path1/?xx=xxx
    var url1 = window.location.href;
    // http://127.0.0.1:8000/path/path1/
    var url = url1.split('?')[0];
    // http:
    var protocol = window.location.protocol;
    // 127.0.0.1:8000
    var host = window.location.host;
    // http://127.0.0.1:8000
    var domain = protocol + '//' + host;
    // /path/path1/
    var path = url.replace(domain,'');
    var menuLis = $(".menu li");
    for(var index=0;index<menuLis.length;index++){
        var li = $(menuLis[index]);
        var a = li.children("a");
        var href1 = a.attr('href');  // /path/path1/?xx=xxx
        var href = href1.split('?')[0];  // /path/path1/
        if(href === path){  // 浏览器url和a标签url比较，相同则表示设置为选中 active
            li.addClass('active');
        }
    }
});