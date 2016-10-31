$(function(){

    window.currentPage = 1;

    $(window).scroll(function() {
        if($(window).scrollTop() == $(document).height() - $(window).height()) {
            // ajax call get data from server and append to the div
            // 获取头像
            $.ajax({
               method:'get',
               url:'/wechat/api/photos?page=' + (currentPage + 1),
               success:function(data){
                   window.currentPage += 1;
                   console.log(data);
                   for(var i = 0; i < data.results.length; i++) {
                       var photo = data.results[i];
                       var fishImg = photo.url;

                       var swiper_html = '';
                       for(var y = 0; y < photo.url.length; y++) {
                           swiper_html += '                <div class="swiper-slide">' +
                        '                    <div class="fishImg">' +
                        '                        <img src="' + photo.url[y] + '"/>' +
                        '                    </div>' +
                        '                </div>'
                       }

                       var html = $('<div class="user" onclick="location=\'/wechat/photos/' + photo.id + '\'/\'">' +
                        '    <div class="userMes">' +
                        '        <div class="userImg">' +
                        '            <img src="' + photo.user.avatar_url +'"/>' +
                        '        </div>' +
                        '        <div class="userName">' + photo.user.nickname + '</div>' +
                        '        <div class="userTime">1分钟前</div>' +
                        '    </div>' +
                        '    <div class="fishMes">' + photo.description + '</div>' +
                        '    <div class="fishDetail">查看详情</div>' +
                        '    <div class="swiper-container">' + swiper_html + '        <!-- If we need pagination -->' +
                        '        <div class="swiper-pagination"></div>' +
                        '' +
                        '        <!-- If we need scrollbar -->' +
                        '        <div class="swiper-scrollbar"></div>' +
                        '    </div>' +
                        '' +
                        '    <div class="userExtraWrap">' +
                        '        <div class="userExtra">' +
                        '            <div class="score">评分可见</div>' +
                        '            <div class="check"><span>' + photo.n_total_watched + '</span>查看</div>' +
                        '            <div class="like"><span>' + photo.n_account_vote + '</span>赞</div>' +
                        '            <div class="store"><span>' + photo.n_avg_mark + '</span>收藏</div>' +
                        '        </div>' +
                        '    </div>' +
                        '</div>');

                       $('.userWrap').append(html);
                   }

               }

            });
        }
    });

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

    var is_positioned = sessionStorage.getItem('is_positioned');
    console.log('is_positioned:', is_positioned);
    if(!is_positioned) {
        console.log('start to get position');
        navigator.geolocation.getCurrentPosition(function(position) {
            console.log('location:', position);
            var data = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude
            };
            $.ajax({
                method: 'post',
                url: '/wechat/api/position',
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: function (data) {
                    sessionStorage.setItem('is_positioned', true);
                    console.log('position success:', data);
                }
            });
        }, function (err) {
            console.warn('ERROR(' + err.code + '): ' + err.message);
        });
    }

    // 点击截图，跳转下一个页面
    $('.modal .button').click(function(){

        $(this).parents(".modal").hide();

        $(".imgSure").show();

        var imgSrc = $('#currentUploadImage').attr('src');

        console.log(imgSrc);

        $("#lastDiv").before('<div class="imgNum"><img src="' + imgSrc +  '"></div>');

        var imgNum = $(".imgNum").length;

        if(imgNum == 4){
            $('#lastDiv').hide();
        }

    });
    //
    $(".classInput").change(function(){
        var success = function (url) {
            console.log('upload success:', url);
            $('#currentUploadImage').attr('src', url + '?imageView2/1/w/750/h/750');
            $(".imgSure").hide();
            $(".modal").show();
        };

        qiniu_upload(this, success, function () {
            console.log('取消上传');
            $(".container").show();
        });
        $(".container").hide();
    });

    $("#imgSureButton").click(function () {
        var text = $("#imgSureText").val();
        var url = [];
        $('.imgNum img').each(function() {
            url.push($(this).attr('src'));
        });

        var data = {
            'description': text,
            'url': url
        };

        $.ajax({
            method: 'POST',
            contentType: 'application/json',
            url: '/wechat/api/photos',
            data: JSON.stringify(data),
            success: function (data) {
                console.log('success', data);
                $(".modal").hide();
                $(".container").show();
            },
            error: function (data) {
                alert('提交失败' + data);
            }
        });
    });

});
