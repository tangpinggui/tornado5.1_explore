$(function () {
    var allDianZan=$('.dianzan');
    allDianZan.click(function () {
        var dianZan = $(this).children('.fa');
        var postId = dianZan.attr('file-id');
        var like_num = parseInt(dianZan.text());
        var onlyRed = $(this).children('.only-red');
        var saved = $(this).children('#saved');
        if (dianZan.css('color') === 'rgb(153, 153, 153)'){
            $.ajax({
                type: 'POST',
                url: '/profile/like',
                dataType: 'json',
                data: {'status': 1, 'file_id': postId},
                success: function (result) {
                    if (result['code'] === 200){
                        dianZan.css('color', 'red');
                        dianZan.text(like_num+1);
                        saved.text('已收藏')
                    }else if (result['code'] === 204){
                        dianZan.css('color', 'red');
                    }
                }
            });
        }else {
            $.ajax({
                type: 'POST',
                url: '/profile/like',
                dataType: 'json',
                data: {'status': 0, 'file_id': postId},
                success: function (result) {
                    if (result['code'] === 200){
                        dianZan.css('color', '');
                        dianZan.text(like_num-1);
                        saved.text('加入宝库')
                        if(onlyRed.length){
                            dianZan.parent().parent().parent().parent().text('')
                        }
                    }
                }
            });
        }
    })
});