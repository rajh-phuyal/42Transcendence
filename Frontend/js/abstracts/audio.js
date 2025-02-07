export default class AudioPlayer {
    // Static property to store songs
    static songs = [
        { mapId: 0, audio: new Audio("../assets/audio/lobby.mp3") },
        { mapId: 1, audio: new Audio("../assets/audio/ufo.mp3") },
        { mapId: 2, audio: new Audio("../assets/audio/lizard-people.mp3") },
        { mapId: 3, audio: new Audio("../assets/audio/snowman.mp3") },
        { mapId: 4, audio: new Audio("../assets/audio/lochness.mp3") }
    ];

    static sounds = [
        { name: "beep1", audio: new Audio("../assets/audio/beep1.mp3") },
        { name: "beep2", audio: new Audio("../assets/audio/beep2.mp3") },
        { name: "paddle", audio: new Audio("../assets/audio/paddle.mp3") },
        { name: "powerup", audio: new Audio("../assets/audio/powerup.mp3") },
        { name: "wall", audio: new Audio("../assets/audio/wall.mp3") },
        { name: "gameover", audio: new Audio("../assets/audio/gameover.mp3") },
        { name: "pause", audio: new Audio("../assets/audio/pause.mp3") },
        { name: "unpause", audio: new Audio("../assets/audio/unpause.mp3") },
        { name: "score", audio: new Audio("../assets/audio/score.mp3") },
        { name: "toggle", audio: new Audio("../assets/audio/toggle.mp3") }
    ];

    static currentSong = null; // Track the currently playing song

    static playSound(name) {
        const sound = this.sounds.find(sound => sound.name === name);
        if (sound)
            sound.audio.play();
        else
            console.error('Sound not found:', name);
    }

    // Static method to play a song
    static play(mapId) {
        console.log('Starting:', mapId);
        const song = this.songs.find(song => song.mapId === mapId);
        if (!song) {
            console.error('Song not found:', mapId);
            return;
        }

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