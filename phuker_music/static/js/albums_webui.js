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
        overwrite: true,
    };
}


createApp({
    components: {
        draggable: vuedraggable,
    },

    setup() {
        const scanStatus = ref('idle');
        const scannedDirs = ref(0);
        const indexFilePath = ref('./index.html');
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

        function deleteAlbum(album) {
            const idx = albums.value.indexOf(album);
            if (idx !== -1) {
                albums.value.splice(idx, 1);
            }
        }

        function addAllAlbums() {
            const existing = new Set(albums.value.map(a => a.album_dir_path));
            let added = 0;
            for (const dirPath of Object.keys(availableAlbums.value).sort()) {
                if (!existing.has(dirPath)) {
                    albums.value.push(createAlbumConfig(dirPath));
                    added++;
                }
            }

            if (added > 0) {
                showToast(`Added ${added} album(s).`, 'success');
            }
        }

        const availableItems = computed(() => {
            return Object.keys(availableAlbums.value).sort().map(dirPath => ({
                album_dir_path: dirPath,
            }));
        });

        async function pollScan() {
            while (true) {
                try {
                    const r = await fetch('/api/scan');
                    const data = await r.json();
                    if (data.status === 'scanning') {
                        scanStatus.value = 'scanning';
                        scannedDirs.value = data.data.scanned_dirs;
                    } else if (data.status === 'done') {
                        scannedDirs.value = data.data.scanned_dirs;
                        indexFilePath.value = data.data.albums_config.albums_index_file_path;
                        albums.value = data.data.albums_config.albums;
                        availableAlbums.value = data.data.available_albums;

                        await sleepAsync(200); // let user see the final scan count before transitioning
                        scanStatus.value = 'done';

                        return;
                    } else {
                        throw new Error(`Invalid status: ${data.status}`);
                    }
                } catch (error) {
                    console.error('pollScan():', error);
                    await sleepAsync(800); // Wait retry
                }

                await sleepAsync(200);
            }
        }

        async function saveConfig() {
            const config = {
                albums_index_file_path: indexFilePath.value,
                albums: albums.value,
            };

            try {
                const r = await fetch('/api/save-config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(config),
                });
                const data = await r.json();
                if (data.status === 'ok') {
                    showToast('Config saved.', 'success');
                } else {
                    throw new Error(data.message);
                }
            } catch (err) {
                showToast(`Failed to save: ${err.message}`, 'error');
            }
        }

        async function regenerate() {
            showToast('Regenerating...', 'info');
            try {
                const r = await fetch('/api/regenerate', { method: 'POST' });
                const data = await r.json();
                if (data.status === 'ok') {
                    showToast('Regeneration complete.', 'success');
                } else {
                    throw new Error(data.message);
                }
            } catch (err) {
                showToast(`Failed to regenerate: ${err.message}`, 'error');
            }
        }

        onMounted(() => {
            pollScan();
        });

        return {
            scanStatus,
            scannedDirs,
            indexFilePath,
            albums,
            availableAlbums,
            availableItems,
            toast,
            getCoverOptions,
            onAlbumsChange,
            deleteAlbum,
            addAllAlbums,
            saveConfig,
            regenerate,
        };
    },
}).mount('#app');
