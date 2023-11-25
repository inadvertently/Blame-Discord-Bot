
import discord


from discord.ext import commands
from discord.enums import ButtonStyle

async def confirm(self:discord.ext.commands.Cog, ctx:discord.ext.commands.Context, msg:discord.Message, invoker:discord.User=None, invoked:discord.User=None, timeout:int=180):
    """Waits for confirmation via reaction from the user before continuing
    Parameters
    ----------
    self : discord.ext.commands.Cog
        Cog the command is invoked in
    ctx : discord.ext.commands.Context
        Command invocation context
    msg : discord.Message
        The message to prompt for confirmation on
    timeout = timeout : int, optional
        How long to wait before timing out (seconds), by default 20
    Returns
    -------
    output : bool or None
        True if user confirms action, False if user does not confirm action, None if confirmation times out
    """
    if invoker == None:
        invoker=ctx.author
    if invoked == None:
        invoked=ctx.author
    view = Confirm(invoker=invoker, invoked=invoked, timeout=timeout)
    await msg.edit(view=view)
    # Wait for the View to stop listening for input...
    await view.wait()
    return view.value

class Confirm(discord.ui.View):
    def __init__(self, invoker:"discord.User|discord.Member", invoked:"discord.User|discord.Member", *, timeout:float=None):
        if timeout is not None:
            super().__init__(timeout=timeout)
        else:
            super().__init__()
        self.value = None
        self.invoker = invoker
        self.invoked = invoked

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Yes", style=ButtonStyle.green)
    async def confirm(self, interaction:discord.Interaction, button:discord.ui.Button):
        await self.confirmation(interaction, True)

    @discord.ui.button(label="No", style=ButtonStyle.red)
    async def cancel(self, interaction:discord.Interaction, button: discord.ui.Button):
        await self.confirmation(interaction, False)

    async def confirmation(self, interaction:discord.Interaction, confirm:bool):
        if confirm:
            if not interaction.user.id == self.invoker.id:
                await interaction.response.send_message(embed=discord.Embed(description=f"<:warn:940732267406454845> {interaction.user.mention}: **You cannot interact with this**", color=int("faa61a", 16)), ephemeral=True)
                return
        else:
            if not interaction.user.id == self.invoker.id:
                if interaction.user.id == self.invoked.id:
                    pass
                else:
                    await interaction.response.send_message(embed=discord.Embed(description=f"<:warn:940732267406454845> {interaction.user.mention}: **You cannot interact with this**", color=int("faa61a", 16)), ephemeral=True)
                    return
        if confirm:
            await interaction.response.defer()
        else:
           await interaction.response.defer()
        self.value = confirm
        self.stop()
#From cop