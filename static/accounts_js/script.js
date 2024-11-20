$(function(){
    $(window).on('load',function(){
        $('.loader').delay(500).fadeOut(800);
        $('.loader-bg').delay(1000).fadeOut(700);
    });
    setTimeout(function(){
        $('.loader-bg').fadeOut(500);
    },5000);
});

$(function() {
    $(".unveil-button").click(function() {
        $(".hidden-value").slideToggle("");
    });
});

// -vhをブラウザに合わせる
const firstViewHeight = () => {
    const vh = window.innerHeight * 0.01;   
    document.getElementById('firstView').style.setProperty('--vh', `${vh}px`);  
  }
  window.addEventListener('resize', firstViewHeight);  


const ham = document.querySelector("#js-hamburger"); //js-hamburgerの要素を取得し、変数hamに格納
const nav = document.querySelector("#js-nav"); //js-navの要素を取得し、変数navに格納
const history = document.querySelector("#js-history");
const historyposts = document.querySelector("#js-historyposts");
const plus = document.querySelector("#js-plus");
const group_list = document.querySelector("#js-group-list");


ham.addEventListener('click', function () { //ハンバーガーメニューをクリックしたら
    ham.classList.toggle('active'); // ハンバーガーメニューにactiveクラスを付け外し
    nav.classList.toggle('active'); // ナビゲーションメニューにactiveクラスを付け外し
});

history.addEventListener('click', function () { //historyをクリックしたら
    history.classList.toggle('active');
    historyposts.classList.toggle('active');
});

plus.addEventListener('click', function () { //plus-btnをクリックしたら
    plus.classList.toggle('active');
    group_list.classList.toggle('active');
});
