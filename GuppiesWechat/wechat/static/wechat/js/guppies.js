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

    })

});
