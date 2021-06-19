const menu = document.querySelector(".menu");
function menuClickHandler(e) {
  const hamburgerIcon = document.querySelector('.hamburgerIcon')
  const menuAside = document.querySelector('.menu__asdide__wrapper')
  const menu = document.querySelector('.menu')
  menuAside.classList.toggle('show_aside');
  console.log(menuAside)
  console.log(hamburgerIcon);
  menu.classList.toggle('move_menu')
  console.log(e.target)
  hamburgerIcon.classList.toggle('open');
}
menu.addEventListener('click',menuClickHandler);


const recommendBtn = document.querySelector('.group__recommend');

const groupFeedBtn = document.querySelector('.group__post');

recommendBtn.addEventListener('click',function(){
  const groupFeed = document.querySelector('.group__feed');
  const groupFeed2 = document.querySelector('.group__feed2');
  groupFeed.classList.remove('group__feed__move');
  groupFeed2.classList.remove('group__feed2__move')
  console.log('recommendBtn');
})


groupFeedBtn.addEventListener('click',function(){
  console.log('groupFeedBtn');
  const groupFeed = document.querySelector('.group__feed');
    const groupFeed2 = document.querySelector('.group__feed2');
  groupFeed.classList.add('group__feed__move');
   groupFeed2.classList.add('group__feed2__move')
})