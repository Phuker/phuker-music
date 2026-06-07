'use strict';

const container = document.getElementById('container');
const albumTitle = document.getElementById('album-title');
const albumDetails = document.getElementById('album-details');
const imgLoading = document.getElementById('imgLoading');
const itemsList = document.getElementById('itemsList');
const btnPlayPrevious = document.getElementById('btnPlayPrevious');
const btnPlayMode = document.getElementById('btnPlayMode');
const imgPlayModeIcon = document.getElementById('imgPlayModeIcon');
const btnShare = document.getElementById('btnShare');
const imgShareIcon = document.getElementById('imgShareIcon');
const btnPlayNext = document.getElementById('btnPlayNext');
const player = document.getElementById('player');
const items = document.getElementsByClassName('item');

const playerCacheNext = new Audio();
const playerSilence = new Audio(SILENCE_AUDIO_DATA_URL);

const MUSIC_PATH_LIST = MUSIC_INFO_LIST.map((music_info) => music_info.path);
const MUSIC_COUNT = MUSIC_INFO_LIST.length;
const RANDOM_INDEX_LIST = shuffleArray([...Array(MUSIC_COUNT).keys()]);
let index = 0;

let shouldAutoplay = false;

const DIR = './';

const PLAY_MODE_LIST = [
    'loop',
    'random',
    'single',
];
const PLAY_MODE_ICON_URL_LIST = [
    IMG_BASE64_DATA_LOOP,
    IMG_BASE64_DATA_RANDOM,
    IMG_BASE64_DATA_SINGLE,
];
let playMode = 'loop'; // value of PLAY_MODE_LIST

const STORAGE_KEY_PATH = STORAGE_KEY_PREFIX + 'path';
const STORAGE_KEY_PLAY_MODE = STORAGE_KEY_PREFIX + 'play_mode';
const STORAGE_VALUE_PATH = localStorage.getItem(STORAGE_KEY_PATH);
const STORAGE_VALUE_PLAY_MODE = localStorage.getItem(STORAGE_KEY_PLAY_MODE);

const URL_PARAM_KEY_PATH = 'path';
const URL_PARAM_KEY_AUTOPLAY = 'autoplay';
const URL_PARAMS = new URLSearchParams(document.location.search);


function my_log(...args) {
    let date = new Date();
    let prefix = `[${date.toLocaleString()} ${date.getMilliseconds().toString().padStart(3, '0')}]`;
    console.log(prefix, ...args);
}


function shuffleArray(array) {
    let result = [...array];
    for (let i = result.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [result[i], result[j]] = [result[j], result[i]];
    }

    return result;
}


// is finite non-negative number
function isValidNumber(n) {
    return typeof n === 'number' && isFinite(n) && n >= 0;
}


function setLoading(show) {
    if (show) {
        items[index].appendChild(imgLoading);
        imgLoading.style['display'] = 'inline';
    } else {
        imgLoading.style['display'] = 'none';
    }
}


function getShareLink() {
    let tmp_link = document.createElement('a');
    tmp_link.href = `?${URL_PARAM_KEY_PATH}=` + encodeURIComponent(MUSIC_INFO_LIST[index].path);
    return tmp_link.href;
}


function getIndex(offset) {
    while (offset < 0) {
        offset += MUSIC_COUNT;
    }

    if (playMode === 'loop') {
        return (index + offset) % MUSIC_COUNT;
    } else if (playMode === 'random') {
        let random_index_list_index = RANDOM_INDEX_LIST.indexOf(index);
        random_index_list_index = (random_index_list_index + offset) % MUSIC_COUNT;
        return RANDOM_INDEX_LIST[random_index_list_index];
    } else if (playMode === 'single') {
        return index;
    }
}


function playIndex(options) {
    let {
        shouldStart = true,
        shouldShowNotification = true,
    } = options || {};

    let { path, name } = MUSIC_INFO_LIST[index];
    my_log(`playIndex(), index: ${typeof index} ${index}, path: ${typeof path} ${path}`);
    player.src = DIR + path;

    if (shouldStart) {
        player.play();
    }

    my_log(`Set localStorage: ${STORAGE_KEY_PATH} = ${typeof path} ${path}`);
    localStorage.setItem(STORAGE_KEY_PATH, path);

    if (shouldShowNotification && 'Notification' in window && Notification.permission === 'granted') {
        let notification = new Notification(name, {
            icon: ALBUM_COVER_FILE,
            body: ALBUM_TITLE,
            requireInteraction: false,
            silent: true,
        });

        notification.addEventListener('click', () => {
            window.focus();
            notification.close();
        });
    }
}


function cacheNext() {
    let indexNext = getIndex(1);
    my_log(`Cache next index: ${typeof indexNext} ${indexNext}`);
    playerCacheNext.src = DIR + MUSIC_INFO_LIST[indexNext].path;
}


function switchPlayMode() {
    let mode_index = PLAY_MODE_LIST.indexOf(playMode);
    mode_index++;
    mode_index %= PLAY_MODE_LIST.length;
    playMode = PLAY_MODE_LIST[mode_index];
    imgPlayModeIcon.src = PLAY_MODE_ICON_URL_LIST[mode_index];

    my_log(`Set localStorage: ${STORAGE_KEY_PLAY_MODE} = ${typeof playMode} ${playMode}`);
    localStorage.setItem(STORAGE_KEY_PLAY_MODE, playMode);

    cacheNext();
}


function playPrevious() {
    my_log('playPrevious()');
    index = getIndex(-1);
    playIndex();
}


function playNext() {
    my_log('playNext()');
    index = getIndex(1);
    playIndex();
}


function playItem(i) {
    if (i === index) {
        if (player.paused) {
            player.play();
        }
    } else {
        index = i;
        playIndex();
    }
}


function clickPlayItem(i) {
    my_log(`clickPlayItem(${i})`);
    playItem(i);
}


function keydownPlayItem(event, i) {
    if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        my_log(`keydownPlayItem(${i}, '${event.key}')`);
        playItem(i);
    }
}


function selectMusic(index) {
    for (let i = 0; i < items.length; i++) {
        items[i].style['color'] = 'inherit';
        items[i].removeAttribute('aria-current');
    }
    items[index].style['color'] = 'blue';
    items[index].setAttribute('aria-current', 'true');
    if (itemsList.scrollTop > (items[index].offsetTop - items[index].clientHeight) ||
        (itemsList.scrollTop + itemsList.clientHeight) < items[index].offsetTop) {
        itemsList.scrollTo(0, items[index].offsetTop - items[index].offsetHeight * 2);
    }

    // Media Session API seems buggy, change document.title for fail safe and compatibility
    document.title = MUSIC_INFO_LIST[index].name;

    navigator.mediaSession.metadata = new MediaMetadata({
        title: MUSIC_INFO_LIST[index].name,
        album: ALBUM_TITLE,
        artwork: [
            {
                src: ALBUM_COVER_FILE,
            },
        ],
    });
}


function init() {
    // load index
    if (STORAGE_VALUE_PATH) {
        index = MUSIC_PATH_LIST.indexOf(STORAGE_VALUE_PATH);
        my_log(`localStorage loaded: ${STORAGE_KEY_PATH}: ${STORAGE_VALUE_PATH}, index: ${index}`);
    }
    if (URL_PARAMS.has(URL_PARAM_KEY_PATH)) {
        index = MUSIC_PATH_LIST.indexOf(URL_PARAMS.get(URL_PARAM_KEY_PATH));
        my_log(`URL param got ${URL_PARAM_KEY_PATH}: ${URL_PARAMS.get(URL_PARAM_KEY_PATH)}, index: ${index}`);
    }

    // not found
    if (index < 0) {
        index = 0;
    }

    // load playMode
    if (STORAGE_VALUE_PLAY_MODE) {
        my_log(`localStorage loaded: ${STORAGE_KEY_PLAY_MODE}: ${typeof STORAGE_VALUE_PLAY_MODE} ${STORAGE_VALUE_PLAY_MODE}`);
        playMode = STORAGE_VALUE_PLAY_MODE;
    }
    imgPlayModeIcon.src = PLAY_MODE_ICON_URL_LIST[PLAY_MODE_LIST.indexOf(playMode)];

    // load shouldAutoplay
    if (URL_PARAMS.has(URL_PARAM_KEY_AUTOPLAY) && URL_PARAMS.get(URL_PARAM_KEY_AUTOPLAY)) {
        shouldAutoplay = true;
        my_log(`URL param got ${URL_PARAM_KEY_AUTOPLAY}`);
    }

    navigator.mediaSession.setActionHandler('play', () => {
        player.play();
    });
    navigator.mediaSession.setActionHandler('pause', () => {
        player.pause();
    });
    navigator.mediaSession.setActionHandler('stop', () => {
        player.pause();
    });
    navigator.mediaSession.setActionHandler('seekbackward', (e) => {
        let seekOffset = isValidNumber(e?.seekOffset) ? e.seekOffset : 10;
        let currentTime = Math.max(player.currentTime - seekOffset, 0);
        player.currentTime = currentTime;
    });
    navigator.mediaSession.setActionHandler('seekforward', (e) => {
        let seekOffset = isValidNumber(e?.seekOffset) ? e.seekOffset : 10;
        let currentTime = Math.min(player.currentTime + seekOffset, player.duration);
        player.currentTime = currentTime;
    });
    navigator.mediaSession.setActionHandler('seekto', (e) => {
        if (!isValidNumber(e?.seekTime)) {
            return;
        }

        player.currentTime = e.seekTime;
    });
    navigator.mediaSession.setActionHandler('previoustrack', playPrevious);
    navigator.mediaSession.setActionHandler('nexttrack', playNext);

    player.addEventListener('ended', () => {
        my_log(`Player event: ended, index: ${typeof index} ${index}`);
        playNext();
    }, false);
    player.addEventListener('play', () => {
        my_log(`Player event: play, index: ${typeof index} ${index}`);
        selectMusic(index);
        setLoading(true);
    }, false);
    player.addEventListener('playing', () => {
        my_log(`Player event: playing, index: ${typeof index} ${index}`);
        selectMusic(index);
        setLoading(false);
        navigator.mediaSession.playbackState = 'playing';
        cacheNext();
    }, false);
    player.addEventListener('error', () => {
        my_log(`Player event: error, index: ${typeof index} ${index}`);
        setLoading(false);
        setTimeout(playNext, 3000);
    }, false);
    player.addEventListener('pause', () => {
        my_log(`Player event: pause, index: ${typeof index} ${index}`);
        setLoading(false);
        navigator.mediaSession.playbackState = 'paused';
    }, false);
    player.addEventListener('waiting', () => {
        my_log(`Player event: waiting, index: ${typeof index} ${index}`);
        setLoading(true);
    }, false);
    player.addEventListener('timeupdate', () => {
        let { duration, playbackRate, currentTime } = player;

        // duration may be NaN at start
        if (!isValidNumber(duration) || !isValidNumber(playbackRate) || !isValidNumber(currentTime)) {
            return;
        }

        // Prevent the page from being suspended during track transitions on mobile.
        // Without continuous audio playback, the browser may suspend the page and stop the next track from playing.
        if (duration - currentTime < 1 && playerSilence.paused) {
            playerSilence.play();
        }

        navigator.mediaSession.setPositionState({
            duration,
            playbackRate,
            position: currentTime,
        });
    }, false);

    selectMusic(index);
    my_log(`Ready, index: ${typeof index} ${index}`);
    my_log(`RANDOM_INDEX_LIST: ${typeof RANDOM_INDEX_LIST} ${JSON.stringify(RANDOM_INDEX_LIST)}`);

    playIndex({
        shouldStart: shouldAutoplay,
        shouldShowNotification: false,
    });

    btnPlayPrevious.addEventListener('click', playPrevious);
    btnPlayMode.addEventListener('click', switchPlayMode);
    btnShare.addEventListener('click', () => {
        navigator.clipboard.writeText(getShareLink());
        imgShareIcon.src = IMG_BASE64_DATA_CHECK;
        setTimeout(() => {
            imgShareIcon.src = IMG_BASE64_DATA_SHARE;
        }, 1500);
    });
    btnPlayNext.addEventListener('click', playNext);

    albumTitle.addEventListener('click', () => {
        albumDetails.showModal();
    });
    albumTitle.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            albumDetails.showModal();
        }
    });

    albumDetails.addEventListener('click', (event) => {
        if (event.target === albumDetails) {
            albumDetails.close();
        }
    });

    window.addEventListener('load', () => {
        if ('Notification' in window && Notification.permission !== 'denied') {
            Notification.requestPermission();
        }

        setTimeout(() => {
            document.getElementById('pageLoading').style['display'] = 'none';
            container.style['visibility'] = 'visible';
            container.style['opacity'] = '1.0';
            player.setAttribute('preload', 'auto');
            selectMusic(index);
        }, 1000);
    });
}

if (MUSIC_COUNT === 0) {
    my_log('No music found');
} else {
    init();
}
