<script lang="ts">
  import {socket} from "../lib/socket";

  function onclick() {
    socket.runCommand("click", '//input[@id="test-element"]')
  }
</script>

<div style="margin: 1em;">
  Whatsapp Sender<br>
  <button {onclick}>CLICK!</button>
  <input type="checkbox" id="test-element" />
</div>

<style>
</style>
