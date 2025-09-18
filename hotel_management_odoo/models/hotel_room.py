# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Vishnu K P (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class HotelRoom(models.Model):
    """Model that holds all details regarding hotel room"""
    _name = 'hotel.room'
    _description = 'Rooms'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @tools.ormcache()
    def _get_default_uom_id(self):
        """Method for getting the default uom id"""
        return self.env.ref('uom.product_uom_unit')

    name = fields.Char(string='Name', help="Name of the Room", index='trigram',
                       required=True, translate=True)
    status = fields.Selection([("available", "Disponible"),
                               ("reserved", "Réservé"),
                               ("occupied", "Occupé"),],
                              default="available", string="Status",
                              help="Status de la salle",
                              tracking=True)
    is_room_avail = fields.Boolean(default=True, string="Disponible",
                                   help="Vérifiez si la chambre est disponible")
    list_price = fields.Float(string='Loyer', digits='Prix du produit',
                              help="Le loyer de la chambre.")
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure',
                             default=_get_default_uom_id, required=True,
                             help="Default unit of measure used for all stock"
                                  " operations.")
    room_image = fields.Image(string="Image de la pièce", max_width=1920,
                              max_height=1920, help='Image of the room')
    taxes_ids = fields.Many2many('account.tax',
                                 'hotel_room_taxes_rel',
                                 'room_id', 'tax_id',
                                 help="Default taxes used when selling the"
                                      " Chambre.", string=' Taxes Clients' ,
                                 domain=[('type_tax_use', '=', 'sale')],
                                 default=lambda self: self.env.company.
                                 account_sale_tax_id)
    room_amenities_ids = fields.Many2many("hotel.amenity",
                                          string="Équipements des chambres",
                                          help="Liste des équipements de la chambre.")
    floor_id = fields.Many2one('hotel.floor', string='Etage',
                               help="Sélection automatique de l’étage",
                               tracking=True)
    user_id = fields.Many2one('res.users', string="User",
                              related='floor_id.user_id',
                              help="Sélectionne automatiquement le responsable",
                              tracking=True)
    room_type = fields.Selection([('single', 'Chambre simple'),
                                  ('double', 'Chambre double'),
                                  ('dormitory', 'Dortoir')],
                                 required=True, string="Type de chambre",
                                 help="Sélectionne automatiquement le type de chambre",
                                 tracking=True,
                                 default="single")
    num_person = fields.Integer(string='Nombre de personnes',
                required=True,
                help="Sélectionne automatiquement le nombre de personnes",
                tracking=True
            )

    description = fields.Html(string='Description', help="Ajouter une description",
                              translate=True)

    @api.constrains("num_person")
    def _check_capacity(self):
        """Check capacity function"""
        for room in self:
            if room.num_person <= 0:
                raise ValidationError(_("Room capacity must be more than 0"))

    @api.onchange("room_type")
    def _onchange_room_type(self):
        """Based on selected room type, number of person will be updated.
        ----------------------------------------
        @param self: object pointer"""
        if self.room_type == "single":
            self.num_person = 1
        elif self.room_type == "double":
            self.num_person = 2
        else:
            self.num_person = 4
