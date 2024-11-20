const inputElem = document.getElementById('id_score'); // input要素
const currentValueElem = document.getElementById('current-value'); // 埋め込む先のspan要素

// -vhをブラウザに合わせる
const firstViewHeight = () => {
  const vh = window.innerHeight * 0.01;   
  document.getElementById('firstView').style.setProperty('--vh', `${vh}px`);  
}
window.addEventListener('resize', firstViewHeight);  


// ボタンクリック時のポップアップアクション
const ham = document.querySelector("#js-hamburger"); //js-hamburgerの要素を取得し、変数hamに格納
const nav = document.querySelector("#js-nav"); //js-navの要素を取得し、変数navに格納
const history = document.querySelector("#js-history");
const historyposts = document.querySelector("#js-historyposts");
const plus = document.querySelector("#js-plus");
const group_list = document.querySelector("#js-group-list");
const summary = document.querySelector("#js-summary");
const thoughts = document.querySelector("#js-thoughts");
const summary_contents = document.querySelector("#js-summary-contents");
const thoughts_contents = document.querySelector("#js-thoughts-contents");


ham.addEventListener('click', function () { //ハンバーガーメニューをクリックしたら
    ham.classList.toggle('active'); // ハンバーガーメニューにactiveクラスを付け外し
    nav.classList.toggle('active'); // ナビゲーションメニューにactiveクラスを付け外し
});

history.addEventListener('click', function () { //historyをクリックしたら
    history.classList.toggle('active');
    historyposts.classList.toggle('active');
});

summary.addEventListener('click', function () { 
  summary.classList.toggle('active');
  summary_contents.classList.toggle('active');
});

thoughts.addEventListener('click', function () { 
  thoughts.classList.toggle('active');
  thoughts_contents.classList.toggle('active');
});


// 現在の値をspanに埋め込む関数
const setCurrentValue = (val) => {
  currentValueElem.innerText = val;
}

// inputイベント時に値をセットする関数
const rangeOnChange = (e) =>{
  setCurrentValue(e.target.value);
}

window.onload = () => {
  if (!inputElem){ return false;}
  inputElem.addEventListener('input', rangeOnChange); // スライダー変化時にイベントを発火
  setCurrentValue(inputElem.value); // ページ読み込み時に値をセット
}

document.addEventListener('DOMContentLoaded', (event) => {
  document.querySelectorAll('.popover').forEach(function(popover) {
    var container = popover.querySelector('.popover-container');
    popover.style.height = container.scrollHeight + 10 + 'px';
  });
});


var app = document.querySelector('title');

var opt;
if (app.outerHTML === '<title>Post Articles</title>') {
  opt = document.querySelector('option[value="/articles/post"]');
} else if (app.outerHTML === '<title>Post Books</title>') {
  opt = document.querySelector('option[value="/books/post"]');
} else if (app.outerHTML === '<title>Post Movies</title>') {
  opt = document.querySelector('option[value="/movies/post"]');
} else if (app.outerHTML === '<title>Post Papers</title>') {
  opt = document.querySelector('option[value="/papers/post"]')
}
opt.selected = true;

document.getElementById('form').select.onchange = function() {
  location.href = document.getElementById('form').select.value;
}
