const { createApp, ref, computed, onMounted } = Vue;


function sleepAsync(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


function createAlbumConfig(dirPath) {
    return {
        album_dir_path: dirPath,
        title: '',
        cover_file: null,
        output_filename: 'player.html',
        recursively: false,
        sort_type: 'filename',
    };
}


createApp({
    components: {
        draggable: vuedraggable,
    },

    setup() {
        const scanStatus = ref('idle');
        const scannedDirs = ref(0);
        const albumsIndexFilePath = ref('./index.html');
        const albums = ref([]);
        const availableAlbums = ref({});
        const toast = ref({ text: '', type: '' });
        let toastTimer = null;

        function showToast(msg, type) {
            toast.value.text = msg;
            toast.value.type = type;
            clearTimeout(toastTimer);
            toastTimer = setTimeout(() => {
                toast.value.type = '';
            }, 4000);
        }

        function getCoverOptions(dirPath, currentCover) {
            const images = (availableAlbums.value[dirPath] || []).map(p => p);
            if (currentCover && !images.includes(currentCover)) {
                images.push(currentCover);
            }

            return images;
        }

        function onAlbumsChange(evt) {
            if (evt.added) {
                Object.assign(albums.value[evt.added.newIndex], createAlbumConfig(evt.added.element.album_dir_path));
            }
        }

        function actionDeleteAlbum(album) {
            const idx = albums.value.indexOf(album);
            if (idx !== -1) {
                albums.value.splice(idx, 1);
            }
        }

        function actionAddAllAlbums() {
            const count = Object.keys(availableAlbums.value).length;
            for (const dirPath of Object.keys(availableAlbums.value).sort()) {
                albums.value.push(createAlbumConfig(dirPath));
            }

            showToast(`Added ${count} album(s)`, 'success');
        }

        const availableItems = computed(() => {
            return Object.keys(availableAlbums.value).sort().map(dirPath => ({
                album_dir_path: dirPath,
            }));
        });

        async function pollScan() {
            while (true) {
                try {
                    const resp = await fetch('/api/scan');
                    const data = await resp.json();
                    if (data.status === 'scanning') {
                        scanStatus.value = 'scanning';
                        scannedDirs.value = data.data.scanned_dirs;
                    } else if (data.status === 'done') {
                        scannedDirs.value = data.data.scanned_dirs;
                        albumsIndexFilePath.value = data.data.albums_config.albums_index_file_path;
                        albums.value = data.data.albums_config.albums;
                        availableAlbums.value = data.data.available_albums;

                        await sleepAsync(200); // let user see the final scan count before transitioning
                        scanStatus.value = 'done';

                        return;
                    } else {
                        throw new Error(JSON.stringify(data));
                    }
                } catch (error) {
                    showToast(`Failed to scan: ${error.message}`, 'error');
                    console.error('pollScan():', error);
                    await sleepAsync(800); // Wait retry
                }

                await sleepAsync(200);
            }
        }

        async function actionPublish() {
            showToast('Saving and generating ...', 'info');

            try {
                const albumsConfig = {
                    albums_index_file_path: albumsIndexFilePath.value,
                    albums: albums.value,
                };

                const resp = await fetch('/api/save-config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(albumsConfig),
                });
                const data = await resp.json();
                if (data.status !== 'ok') {
                    throw new Error(JSON.stringify(data));
                }
            } catch (error) {
                showToast(`Failed to save: ${error.message}`, 'error');
                console.error('actionPublish():', error);
                return;
            }

            try {
                const resp = await fetch('/api/regenerate', { method: 'POST' });
                const data = await resp.json();
                if (data.status !== 'ok') {
                    throw new Error(JSON.stringify(data));
                }
            } catch (error) {
                showToast(`Failed to generate: ${error.message}`, 'error');
                console.error('actionPublish():', error);
                return;
            }

            showToast('Done', 'success');
        }

        onMounted(() => {
            pollScan();
        });

        return {
            scanStatus,
            scannedDirs,
            albumsIndexFilePath,
            albums,
            availableAlbums,
            availableItems,
            toast,
            getCoverOptions,
            onAlbumsChange,
            actionDeleteAlbum,
            actionAddAllAlbums,
            actionPublish,
        };
    },
}).mount('#app');
