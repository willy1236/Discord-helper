from dataclasses import dataclass, field
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional, TypedDict

from discord import Bot
from sqlalchemy import (BigInteger, Column, DateTime, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.orm import declarative_base
from sqlmodel import Field, Relationship, SQLModel

from ..settings import tz
from ..types import *
from ..utilities import BotEmbed, ChoiceList
from .BaseModel import ListObject

if TYPE_CHECKING:
    from ..database import SQLEngine

Base = declarative_base()

class Student(SQLModel, table=True):
    __tablename__ = 'students'
    __table_args__ = {'schema': 'database'}
    
    id: int = Field(sa_column=Column(Integer, primary_key=True))
    name: str = Field(sa_column=Column(String(255)))
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=lambda: datetime.now(tz)))
    school_id: int | None = Field(foreign_key="database.schools.id")

    school: "School" = Relationship(back_populates="students")

class School(SQLModel, table=True):
    __tablename__ = 'schools'
    __table_args__ = {'schema': 'database'}

    id: int = Field(primary_key=True)
    name: str

    students: list[Student] = Relationship(back_populates="school")

class CloudUser(SQLModel, table=True):
    __tablename__ = 'cloud_user'
    __table_args__ = {'schema': 'stardb_user'}

    id: str | None
    discord_id: int = Field(sa_column=Column(BigInteger, primary_key=True, autoincrement=False))
    email: str | None
    drive_share_id: str | None
    twitch_id: int | None

class DiscordUser(SQLModel, table=True):
    __tablename__ = "user_discord"
    __table_args__ = {'schema': 'stardb_user'}

    discord_id: int = Field(sa_column=Column(BigInteger, primary_key=True, autoincrement=False))
    name: str | None
    max_sign_consecutive_days: int | None
    meatball_times: int | None
    guaranteed: int | None
    registrations_id: int | None = Field(foreign_key="stardb_idbase.discord_registrations.registrations_id")
    
    registration: "DiscordRegistration" = Relationship(back_populates="members")

class UserPoint(SQLModel, table=True):
    __tablename__ = "user_point"
    __table_args__ = {'schema': 'stardb_user'}

    discord_id: int = Field(sa_column=Column(BigInteger, primary_key=True, autoincrement=False))
    stardust: int | None = Field(default=0)
    point: int | None = Field(default=0)
    rcoin: int | None = Field(default=0)

class UserPoll(SQLModel, table=True):
    __tablename__ = "user_poll"
    __table_args__ = {'schema': 'stardb_user'}
    
    poll_id: int = Field(primary_key=True, foreign_key="stardb_basic.poll_data.poll_id")
    discord_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    vote_option: int = Field(primary_key=True, foreign_key="stardb_basic.poll_options.option_id")
    vote_at: datetime
    vote_magnification: int = Field(default=1)

class UserAccount(SQLModel, table=True):
    __tablename__ = "user_account"
    __table_args__ = {'schema': 'stardb_user'}

    main_account: int = Field(primary_key=True)
    alternate_account: int = Field(primary_key=True)

class UserParty(SQLModel, table=True):
    __tablename__ = "user_party"
    __table_args__ = {'schema': 'stardb_user'}
    
    discord_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    party_id: int = Field(primary_key=True, foreign_key="stardb_idbase.party_datas.party_id")
    
    party: "Party" = Relationship(back_populates="members")

class UserModerate(SQLModel, table=True):
    __tablename__ = "user_moderate"
    __table_args__ = {'schema': 'stardb_user'}

    warning_id: int = Field(primary_key=True, default=None)
    discord_id: int = Field(sa_column=Column(BigInteger))
    moderate_type: WarningType = Field(sa_column=Column(Integer, primary_key=True))
    moderate_user: int
    create_guild: int
    create_time: int
    reason: str | None
    last_time: str | None
    guild_only: bool | None
    officially_given: bool | None

    def embed(self,bot:Bot):
        user = bot.get_user(self.discord_id)
        moderate_user = bot.get_user(self.moderate_user)
        guild = bot.get_guild(self.create_guild)
        
        name = f'{user.name} 的警告單'
        description = f"**編號:{self.warning_id} ({ChoiceList.get_tw(self.moderate_type,'warning_type')})**\n被警告用戶：{user.mention}\n管理員：{guild.name}/{moderate_user.mention}\n原因：{self.reason}\n時間：{self.create_time}"
        if self.officially_given:
            description += "\n官方警告"
        if self.guild_only:
            description += "\n伺服器區域警告"
        embed = BotEmbed.general(name=name,icon_url=user.display_avatar.url,description=description)
        return embed
    
    def display_embed_field(self,bot:Bot):
            moderate_user = bot.get_user(self.moderate_user)
            guild = bot.get_guild(self.create_guild)
            name = f"編號: {self.warning_id} ({ChoiceList.get_tw(self.moderate_type,'warning_type')})"
            value = f"{guild.name}/{moderate_user.mention}\n{self.reason}\n{self.create_time}"
            if self.officially_given:
                value += "\n官方警告"
            if self.guild_only:
                value += "\n伺服器區域警告"
            return name, value

class RoleSave(SQLModel, table=True):
    __tablename__ = "role_save"
    __table_args__ = {'schema': 'stardb_user'}

    discord_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    role_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    role_name: str
    time: date

class UserPet(SQLModel, table=True):
    __tablename__ = "user_pet"
    __table_args__ = {'schema': 'stardb_user'}

    discord_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    pet_species: str
    pet_name: str
    food: int | None

class NotifyChannel(SQLModel, table=True):
    __tablename__ = "notify_channel"
    __table_args__ = {'schema': 'stardb_basic'}
    
    guild_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    notify_type: NotifyChannelType = Field(sa_column=Column(Integer, primary_key=True))
    channel_id: int = Field(sa_column=Column(BigInteger))
    role_id: int | None = Field(sa_column=Column(BigInteger))

class NotifyCommunity(SQLModel, table=True):
    __tablename__ = "notify_community"
    __table_args__ = {'schema': 'stardb_basic'}
    
    notify_type: NotifyCommunityType = Field(sa_column=Column(Integer, primary_key=True))
    notify_name: str = Field(primary_key=True)
    guild_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    display_name: str
    channel_id: int = Field(sa_column=Column(BigInteger))
    role_id: int | None = Field(sa_column=Column(BigInteger))

class DynamicChannel(SQLModel, table=True):
    __tablename__ = "dynamic_channel"
    __table_args__ = {'schema': 'stardb_basic'}
    
    channel_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    discord_id: int = Field(sa_column=Column(BigInteger))
    guild_id: int = Field(sa_column=Column(BigInteger))
    created_at: datetime

class Poll(SQLModel, table=True):
    __tablename__ = "poll_data"
    __table_args__ = {'schema': 'stardb_basic'}

    poll_id: int = Field(default=None, primary_key=True)
    title: str
    created_user: int = Field(sa_column=Column(BigInteger))
    created_at: datetime
    is_on: bool
    message_id: int
    guild_id: int = Field(sa_column=Column(BigInteger))
    ban_alternate_account_voting: bool
    show_name: bool
    check_results_in_advance: bool
    results_only_initiator: bool
    number_of_user_votes: int

class PollOption(SQLModel, table=True):
    __tablename__ = "poll_options"
    __table_args__ = {'schema': 'stardb_basic'}

    poll_id: int = Field(primary_key=True, foreign_key="stardb_basic.poll_data.poll_id")
    option_id: int = Field(primary_key=True)
    option_name: str

class PollRole(SQLModel, table=True):
    __tablename__ = "poll_role"
    __table_args__ = {'schema': 'stardb_basic'}

    poll_id: int = Field(primary_key=True, foreign_key="stardb_basic.poll_data.poll_id")
    role_id: int = Field(sa_column=Column(BigInteger))
    role_type: int
    role_magnification: int

class TwitchBotJoinChannel(SQLModel, table=True):
    __tablename__ = "twitch_bot_join_channel"
    __table_args__ = {'schema': 'stardb_basic'}
    
    twitch_id: int = Field(primary_key=True)
    action_channel_id: int | None = Field(sa_column=Column(BigInteger))

class Party(SQLModel, table=True):
    __tablename__ = "party_datas"
    __table_args__ = {'schema': 'stardb_idbase'}

    party_id: int = Field(primary_key=True)
    party_name: str
    role_id: int
    creator_id: int
    created_at: datetime
    
    members: list[UserParty] = Relationship(back_populates="party")

class DiscordRegistration(SQLModel, table=True):
    __tablename__ = "discord_registrations"
    __table_args__ = {'schema': 'stardb_idbase'}
    
    registrations_id: int = Field(primary_key=True)
    guild_id: int = Field(sa_column=Column(BigInteger))
    role_id: int = Field(sa_column=Column(BigInteger))

    members: list[DiscordUser] = Relationship(back_populates="registration")

class TRPGStoryPlot(SQLModel, table=True):
    __tablename__ = "trpg_storyplots"
    __table_args__ = {'schema': 'stardb_idbase'}

    id: int = Field(primary_key=True)
    title: str
    content: str = Field(sa_column=Column(Text))
    options: list["TRPGStoryOption"] = Relationship(back_populates="plot")

class TRPGStoryOption(SQLModel, table=True):
    __tablename__ = "trpg_plot_options"
    __table_args__ = {'schema': 'stardb_idbase'}

    plot_id: int = Field(primary_key=True, foreign_key="stardb_idbase.trpg_storyplots.id")
    option_id: int = Field(primary_key=True)
    option_title: str
    lead_to_plot: int | None
    check_ability: int | None
    san_check_fall_dice: str | None
    success_plot: int | None
    fail_plot: int | None
    plot: TRPGStoryPlot = Relationship(back_populates="options")

class TRPGCharacter(SQLModel, table=True):
    __tablename__ = "trpg_characters"
    __table_args__ = {'schema': 'stardb_idbase'}

    discord_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    character_name: str

    abilities: list["TRPGCharacterAbility"] = Relationship(back_populates="character")

class TRPGCharacterAbility(SQLModel, table=True):
    __tablename__ = "trpg_character_abilities"
    __table_args__ = {'schema': 'stardb_idbase'}

    discord_id: int = Field(sa_column=Column(BigInteger, ForeignKey("stardb_idbase.trpg_characters.discord_id"), primary_key=True))
    ability_id: int = Field(primary_key=True, foreign_key="stardb_idbase.trpg_abilities.ability_id")
    san_lower_limit: int | None
    value: int

    character: TRPGCharacter = Relationship(back_populates="abilities")
    ability: "TRPGAbility" = Relationship(back_populates="characters")

class TRPGAbility(SQLModel, table=True):
    __tablename__ = "trpg_abilities"
    __table_args__ = {'schema': 'stardb_idbase'}

    ability_id: int = Field(primary_key=True)
    ability_name: str

    characters: list[TRPGCharacterAbility] = Relationship(back_populates="ability")

class BackupRole(SQLModel, table=True):
    __tablename__ = "roles_backup"
    __table_args__ = {'schema': 'stardb_backup'}

    role_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    role_name: str
    created_at: datetime
    guild_id: int = Field(sa_column=Column(BigInteger))
    colour_r: int
    colour_g: int
    colour_b: int
    description: str

    members: list["BackupRoleUser"] = Relationship(back_populates="role")
    
    def embed(self, bot:Bot):
        embed = BotEmbed.simple(self.role_name,self.description)
        embed.add_field(name="創建於", value=self.created_at.strftime("%Y/%m/%d %H:%M:%S"))
        embed.add_field(name="顏色", value=f"({self.colour_r}, {self.colour_g}, {self.colour_b})")
        if bot and self.members:
            user_list = list()
            for user in self.members:
                user = bot.get_user(user.discord_id)
                if user:
                    user_list.append(user.mention)
            embed.add_field(name="成員", value=",".join(user_list),inline=False)

        return embed

class BackupRoleUser(SQLModel, table=True):
    __tablename__ = "role_user_backup"
    __table_args__ = {'schema': 'stardb_backup'}
    
    role_id: int = Field(sa_column=Column(BigInteger, ForeignKey("stardb_backup.roles_backup.role_id"), primary_key=True))
    discord_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    role: BackupRole = Relationship(back_populates="members")

class OAuth2Token(SQLModel, table=True):
    __tablename__ = "oauth_token"
    __table_args__ = {'schema': 'stardb_tokens'}

    user_id: str = Field(primary_key=True)
    type: CommunityType = Field(sa_column=Column(Integer, primary_key=True))
    access_token: str
    refresh_token: str
    expires_at: datetime

class BotToken(SQLModel, table=True):
    __tablename__ = "bot_token"
    __table_args__ = {'schema': 'stardb_tokens'}

    api_type: CommunityType = Field(sa_column=Column(Integer, primary_key=True))
    id: int | None = Field(sa_column=Column(Integer, primary_key=True))
    client_id: str | None
    client_secret: str | None
    access_token: str | None
    refresh_token: str | None
    revoke_token: str | None
    redirect_uri: str | None
    callback_uri: str | None

class WarningList(ListObject):
    if TYPE_CHECKING:
        items: list[UserModerate]
        discord_id: int

    def __init__(self,items:list, discord_id:int):
        super().__init__(items)
        self.discord_id = discord_id
    
    def display(self,bot:Bot):
        user = bot.get_user(self.discord_id)
        embed = BotEmbed.general(f'{user.name} 的警告單列表（共{len(self.items)}筆）',user.display_avatar.url)
        for i in self.items:
            name, value = i.display_embed_field(bot)
            embed.add_field(name=name,value=value)
        return embed