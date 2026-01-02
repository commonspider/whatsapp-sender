<script lang="ts">
  import { sender } from "../singletons";

  const packet_num = sender.packets_num;
  const packet_sent = sender.packets_sent;
</script>

<div
  style="margin: 0.5em; padding: 0.5em; border: 3px solid green; background: lightgreen; border-radius: 10px;"
>
  {#if $packet_num > 0}
    {#if $packet_sent < $packet_num}
      Whatsapp Sender: {$packet_sent} / {$packet_num}
    {:else}
      Whatsapp Sender: Finito!
    {/if}
  {:else}
    Whatsapp Sender: in attesa
  {/if}
</div>
