$(function(){

    // 图片预览
    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();

            reader.onload = function (e) {
                $('#blah').attr('src', e.target.result);
            };

            reader.readAsDataURL(input.files[0]);
        }
    }
    $("#imgInp").change(function(){
        readURL(this);
        $('.alertBox1').show();
        $('body').css('overflow','hidden');
        // qiniu_upload(this);
    });

    // 确认开晒
    $(document).on('click','#imgCut1',function(){

        $('.alertBox1').hide();
        $('.alertBox2').show();
        $('body').css('overflow','hidden');

    });

    $(document).on('click','#imgCut2',function(){

        $('.alertBox2').hide();
        $('body').css('overflow','auto');

    });

    //// 获取头像
    //$.ajax({
    //    method:'get',
    //    url:'/wechat/api/photos',
    //    success:function(data){
    //        console.log(data);
    //        for(var i = 0; i < data.results.length; i++) {
    //            var imgUrl = data.results[i].user.avatar_url;
    //            var uerName = data.results[i].user.nickname;
    //            var imgInfo = data.results[i].description;
    //            var fishImg = data.results[i].url;
    //            var getWatch = data.results[i].n_total_watched;
    //            var getGood = data.results[i].n_account_vote;
    //            var getScore = data.results[i].n_total_mark ;
    //
    //            var html = $('<div class="user">' +
    //                '    <a href="#">' +
    //                '        <div class="borderColor"></div>' +
    //                '        <div class="userInfo">' +
    //                '            <div class="userImg"><img src="' + imgUrl + '"/></div>' +
    //                '            <span class="userName">' + uerName + '</span>' +
    //                '            <span class="userTime">1分钟前</span>' +
    //                '            <div class="userText">' + imgInfo + '</div>' +
    //                '        </div>' +
    //                '        <div class="guppiesImg">' +
    //                '            <img src="' + fishImg + '"/>' +
    //                '        </div>' +
    //                '        <div class="score">' +
    //                '            <span>查看&nbsp;<em>' + getWatch + '</em></span>' +
    //                '            <span>点赞&nbsp;<em>' + getGood + '</em></span>' +
    //                '            <span>评分&nbsp;<em class="fontColor">' + getScore + '</em></span>' +
    //                '        </div>' +
    //                '    </a>' +
    //                '</div>');
    //
    //            $('.doc').append(html);
    //        }
    //
    //    }
    //
    //});

});
