const { createApp, ref, computed, onMounted } = Vue;


function sleepAsync(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


async function pollFetch(resource, options, onRunning) {
    while (true) {
        const resp = await fetch(resource, options);
        const data = await resp.json();

        if (data.status === 'running') {
            if (onRunning) {
                onRunning(data);
            }

            await sleepAsync(300);
        } else if (data.status === 'done') {
            return data;
        } else {
            throw new Error(JSON.stringify(data));
        }
    }
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
        const albumsDirPath = ref('.');
        const albumsIndexFilename = ref('index.html');
        const isPublishing = ref(false);
        const albums = ref([]);
        const availableAlbums = ref({});
        const toasts = ref([]);
        let toastId = 0;

        function showToast(msg, type, duration = 4000) {
            const id = ++toastId;
            toasts.value.push({ id: id, text: msg, type: type });
            setTimeout(() => {
                const index = toasts.value.findIndex((toast) => (toast.id === id));
                if (index !== -1) {
                    toasts.value.splice(index, 1);
                }
            }, duration);
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
            const index = albums.value.indexOf(album);
            if (index !== -1) {
                albums.value.splice(index, 1);
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
            try {
                const data = await pollFetch('/api/scan', { method: 'POST' }, (data) => {
                    scanStatus.value = 'running';
                    scannedDirs.value = data.data.scanned_dirs;
                });

                scannedDirs.value = data.data.scanned_dirs;
                albumsDirPath.value = data.data.albums_config.albums_dir_path;
                albumsIndexFilename.value = data.data.albums_config.albums_index_filename;
                albums.value = data.data.albums_config.albums;
                availableAlbums.value = data.data.available_albums;

                await sleepAsync(200); // let user see the final scan count before transitioning
                scanStatus.value = 'done';
            } catch (error) {
                showToast(`Failed to scan: ${error.message}`, 'error');
                console.error('pollScan():', error);
            }
        }

        async function _actionPublish() {
            showToast('Saving ...', 'info');
            try {
                const albumsConfig = {
                    albums_dir_path: albumsDirPath.value,
                    albums_index_filename: albumsIndexFilename.value,
                    albums: albums.value,
                };

                const resp = await fetch('/api/save-config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(albumsConfig),
                });
                const data = await resp.json();
                if (data.status !== 'done') {
                    throw new Error(JSON.stringify(data));
                }
            } catch (error) {
                showToast(`Failed to save: ${error.message}`, 'error');
                console.error('actionPublish():', error);
                return;
            }

            showToast('Generating ...', 'info');
            try {
                await pollFetch('/api/generate', { method: 'POST' });
            } catch (error) {
                showToast(`Failed to generate: ${error.message}`, 'error');
                console.error('actionPublish():', error);
                return;
            }

            showToast('Done', 'success');
        }

        function actionPublish() {
            isPublishing.value = true;
            _actionPublish().finally(() => {
                isPublishing.value = false;
            });
        }

        onMounted(() => {
            pollScan();
        });

        return {
            scanStatus,
            scannedDirs,
            albumsDirPath,
            albumsIndexFilename,
            isPublishing,
            albums,
            availableAlbums,
            availableItems,
            toasts,
            getCoverOptions,
            onAlbumsChange,
            actionDeleteAlbum,
            actionAddAllAlbums,
            actionPublish,
        };
    },
}).mount('#app');
