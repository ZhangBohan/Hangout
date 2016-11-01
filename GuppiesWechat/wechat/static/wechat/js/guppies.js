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
                $(".imgSure").hide();
                $(".container").show();
            },
            error: function (data) {
                alert('提交失败' +  + JSON.stringify(data));
            }
        });
    });

});
