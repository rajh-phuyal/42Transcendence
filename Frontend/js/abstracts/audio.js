export default class AudioPlayer {
    // Static property to store songs
    static songs = [
        //window.location.origin + '/assets/
        { mapId: 1, audio: new Audio("../assets/audio/ufo.mp3") },
        { mapId: 2, audio: new Audio("../assets/audio/lizard-people.mp3") },
        { mapId: 3, audio: new Audio("../assets/audio/snowman.mp3") },
        { mapId: 4, audio: new Audio("../assets/audio/lochness.mp3") }
    ];

    static currentSong = null; // Track the currently playing song

    // Static method to play a song
    static play(mapId) {
        console.log('Starting:', mapId);
        const song = this.songs.find(song => song.mapId === mapId);
        if (!song)
            console.error('Song not found:', mapId);

        // Stop the currently playing song if there is one
        this.stop();

        // Play the new song
        song.audio.play();
        this.currentSong = song; // Store reference to currently playing song
        console.log('Playing:', song);
    }

    // Static method to stop playing
    static stop() {
        if (this.currentSong) {
            this.currentSong.audio.pause();
            this.currentSong.audio.currentTime = 0; // Reset audio to start
            this.currentSong = null; // Clear reference
        }
    }
}