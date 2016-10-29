var Qiniu_UploadUrl = "https://up.qbox.me/";

var qiniu_upload = function (img_input, on_success, on_error) {
    //普通上传
    var Qiniu_upload = function (f, token, key, success_callback) {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', Qiniu_UploadUrl, true);
        var formData;
        formData = new FormData();
        if (key !== null && key !== undefined) formData.append('key', key);
        formData.append('token', token);
        formData.append('file', f);

        xhr.onreadystatechange = function (response) {
            if (xhr.readyState == 4 && xhr.status == 200 && xhr.responseText != "") {
                var blkRet = JSON.parse(xhr.responseText);
                console && console.log(blkRet);
                success_callback();
            } else if (xhr.status != 200 && xhr.responseText) {
                alert('上传图片失败!' + xhr.responseText);
                on_error();
            }
        };
        xhr.send(formData);
    };

    $.ajax({
        method: 'POST',
        url: '/wechat/api/uploader',
        success: function (data) {
            var token = data.token;
            var files = img_input.files;
            var key = data.key;
            var url = data.url;

            if (files.length > 0) {
                Qiniu_upload(files[0], token, key, function () {
                    console.log('upload success');
                    on_success(url);
                });

            } else {
                on_error();
            }
        }
    });

};
