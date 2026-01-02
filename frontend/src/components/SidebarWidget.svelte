<script lang="ts">
  import { log, sender } from "../singletons";
  import { derived } from "svelte/store";

  const packet_num = sender.packets_num;
  const packet_sent = sender.packets_sent;
  const perc = derived(
    [packet_num, packet_sent],
    ([num, sent]) => (sent * 100) / num,
  );
  const countdown = sender.delayer.countdown;
  const lines = log.lines;
</script>

<div style="width: 100%; margin-top: 2em; margin-bottom: 2em;">
  {#if $packet_num > 0}
    {#if $packet_sent < $packet_num}
      Whatsapp Sender: [ {$packet_sent} / {$packet_num} ]
      {#if $countdown !== undefined}
        Cooldown: {Math.round($countdown / 1000)}...
      {/if}
      <br />
    {:else}
      Whatsapp Sender: Finito!<br />
    {/if}
    <progress
      value={$perc}
      max="100"
      style="margin-top: 1em; margin-bottom: 1em"
    ></progress>
  {:else}
    Whatsapp Sender: In attesa<br />
  {/if}
  {#each $lines as line}
    {line}<br />
  {/each}
</div>
